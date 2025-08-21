import os, zipfile
from typing import List, Dict, Tuple, Optional
import numpy as np
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from pytubefix import YouTube
from faster_whisper import WhisperModel

from subs_utils import parse_srt_segments, segs_to_text, words_from_segs, write_ass_karaoke, burn_ass_to_video, write_srt_for_range
from video_utils import crop_center, crop_face_track
from llm_utils import pick_highlights, generate_titles_from_highlights


def download_youtube(url: str) -> Optional[str]:
    try:
        yt = YouTube(url)
        stream = (yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first() or
                  yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first())
        os.makedirs('videos', exist_ok=True)
        return stream.download(output_path='videos')
    except Exception:
        return None


def transcribe(video_path: str):
    try:
        import torch
        device = 'cuda' if getattr(torch, 'cuda', None) and torch.cuda.is_available() else 'cpu'
    except Exception:
        device = 'cpu'
    model = WhisperModel('base.en', device=device, compute_type='float16' if device=='cuda' else 'int8')
    seg_iter, _ = model.transcribe(video_path, beam_size=5, language='en', word_timestamps=True)
    segs = []
    for s in seg_iter:
        words = []
        if getattr(s, 'words', None):
            for w in s.words:
                words.append({'start': float(w.start), 'end': float(w.end), 'text': w.word})
        segs.append({'start': float(s.start), 'end': float(s.end), 'text': s.text.strip(), 'words': words})
    return segs, segs_to_text(segs)


def add_title_overlay(video_path: str, out_path: str, title_text: str, platform: str = 'TikTok'):
    with VideoFileClip(video_path) as v:
        w, h = v.w, v.h
        margin = int(0.10*h if platform == 'TikTok' else 0.08*h)
        txt = TextClip(title_text, font='FreeMono', fontsize=max(36, int(h*0.05)), color='white', stroke_color='black', stroke_width=2)
        txt = txt.set_pos(('center', margin)).set_duration(v.duration)
        CompositeVideoClip([v, txt]).write_videofile(out_path, codec='libx264', audio_codec='aac')


def add_watermark(video_path: str, wm_path: str, out_path: str):
    with VideoFileClip(video_path) as v:
        wm = (ImageClip(wm_path).set_duration(v.duration).resize(height=int(max(48, v.h*0.06))).set_pos(('right','top')))
        CompositeVideoClip([v, wm]).write_videofile(out_path, codec='libx264', audio_codec='aac')


def generate_pipeline(youtube_url, video_file, srt_file, provider, openai_key, gemini_key, min_len, max_len, max_clips, aspect, crop_mode, karaoke, export_srt, title_mode, custom_title, platform, out_prefix, watermark_file, seo_text: str = '', logger=print):
    # Get path
    path = None
    if youtube_url:
        path = download_youtube(youtube_url)
        if path: logger(f"Downloaded YouTube -> {path}")
    if not path and video_file is not None:
        path = video_file.name
    if not path:
        logger('No video provided.')
        return None

    # Transcription
    if srt_file is not None:
        segs = parse_srt_segments(srt_file.name)
        text = segs_to_text(segs)
        segs = words_from_segs(segs)
    else:
        segs, text = transcribe(path)
    if not text:
        logger('Empty transcription')
        return None

    api_key = openai_key if provider == 'OpenAI' else gemini_key
    if not api_key:
        logger(f"Missing API key for {provider}. Please provide a valid key.")
        return None
    highs = pick_highlights(text, provider, api_key, int(max_clips), int(min_len), int(max_len))
    if not highs:
        logger('No highlights found.')
        return None

    if title_mode == 'Auto':
        titles = generate_titles_from_highlights(highs, provider, api_key)
    elif title_mode == 'Custom':
        titles = [custom_title or ''] * len(highs)
    else:
        titles = [''] * len(highs)

    out_pref = out_prefix or 'short'
    outputs: List[str] = []
    srt_outputs: List[str] = []

    for i, h in enumerate(highs, start=1):
        s, e = float(h['start']), float(h['end'])
        clip_path = f"{out_pref}_{i}.mp4"
        with VideoFileClip(path) as v:
            sub = v.subclip(s, e)
            if crop_mode == 'Face-track':
                sub = crop_face_track(sub, aspect)
            else:
                sub = crop_center(sub, aspect)
            logger(f"Rendering clip {i}: {s:.2f}s to {e:.2f}s")
            sub.write_videofile(clip_path, codec='libx264', audio_codec='aac')

        # Optional per-clip SRT export (before any overlays/watermarks)
        if export_srt and segs:
            try:
                srt_path = f"{out_pref}_{i}.srt"
                write_srt_for_range(segs, srt_path, s, e)
                srt_outputs.append(srt_path)
            except Exception as ex:
                logger(f"SRT export failed for clip {i}: {ex}")

        cur = clip_path
        if karaoke and segs:
            ass = f"{out_pref}_{i}.ass"
            res = (1080,1920) if aspect == '9:16' else (1920,1080)
            write_ass_karaoke(segs, ass, s, e, res)
            kara = f"{out_pref}_{i}_karaoke.mp4"
            try:
                burn_ass_to_video(cur, ass, kara)
                cur = kara
            except Exception as ex:
                logger(f"Karaoke burn failed: {ex}")

        ttl = titles[i-1] if i-1 < len(titles) else ''
        if ttl:
            ttl_out = f"{out_pref}_{i}_title.mp4"
            try:
                add_title_overlay(cur, ttl_out, ttl, platform)
                cur = ttl_out
            except Exception as ex:
                logger(f"Title overlay failed: {ex}")

        if watermark_file is not None:
            wm_out = f"{out_pref}_{i}_wm.mp4"
            try:
                add_watermark(cur, watermark_file.name, wm_out)
                cur = wm_out
            except Exception as ex:
                logger(f"Watermark failed: {ex}")

        outputs.append(cur)

    # Write SEO/description if provided
    if seo_text:
        try:
            with open(f"{out_pref}_description.txt", 'w', encoding='utf-8') as f:
                f.write(seo_text.strip() + "\n")
        except Exception:
            pass

    zip_path = f"{out_pref}_results.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        for f in outputs:
            if os.path.exists(f):
                z.write(f)
        # Add any SRTs generated per-clip
        for srt in srt_outputs:
            if os.path.exists(srt):
                z.write(srt)
        if export_srt and segs:
            with open('transcription.txt','w',encoding='utf-8') as f:
                f.write(text)
            z.write('transcription.txt')
        if seo_text and os.path.exists(f"{out_pref}_description.txt"):
            z.write(f"{out_pref}_description.txt")
    return zip_path
