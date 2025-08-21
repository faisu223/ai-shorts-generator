# AI Shorts Generator — Colab + Gradio

Generate social-ready short clips from long videos with a simple, beginner-friendly Gradio UI that runs fully in Google Colab.

Features
- Upload a long video (or paste a YouTube URL)
- Optional SRT upload; if provided, Whisper transcription is skipped
- Choose target short length, max clips, aspect ratio (9:16/16:9/1:1)
- Crop mode: Center or Face-track (OpenCV Haar cascade)
- Burn karaoke-style subtitles (ASS) or export SRT files
- Auto-generate titles using OpenAI or Gemini, or provide a custom title
- Optional watermark/logo overlay
- Enter API keys in the UI (no .env)
- Download a ZIP including clips, per-clip SRTs, full transcription, and optional SEO text

Quick start (Colab)
1. Upload this repo to GitHub and open Colab.
2. Open the notebook `Colab_Gradio_AI_Shorts.ipynb` in Colab.
3. Run the Setup cell (installs ffmpeg, Python deps, face cascade).
4. Run the UI cell and use the Gradio interface.

Notes
- GPU is recommended for faster Whisper transcription and video processing.
- The face-track crop falls back to center crop if no face is detected.
- API provider choices: OpenAI (gpt-4o-mini) or Google Gemini (2.5-flash).

Repo structure
- `pipeline_advanced.py` — main pipeline to cut clips, add subtitles/titles/watermark, zip outputs
- `llm_utils.py` — highlight selection + title generation (OpenAI/Gemini)
- `subs_utils.py` — SRT parsing, ASS karaoke generation, ffmpeg burning, per-clip SRT export
- `video_utils.py` — aspect cropping and simple face tracking
- `Colab_Gradio_AI_Shorts.ipynb` — ready-to-run notebook with Gradio UI

Run locally (CLI)
A lightweight CLI is included to run the pipeline without Colab/Gradio.

Prerequisites
- ffmpeg installed and available on PATH
- Python 3.9+
- (Optional) ImageMagick if MoviePy's TextClip requires it on your system

Setup
```
python -m venv .venv
. .venv/bin/activate  # on Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Basic usage
- Using a local file:
```
python run_pipeline.py \
  --video-file path/to/long_video.mp4 \
  --provider OpenAI --openai-key YOUR_OPENAI_KEY \
  --min-len 20 --max-len 50 --max-clips 3 \
  --aspect 9:16 --crop-mode Face-track \
  --karaoke --export-srt \
  --title-mode Auto \
  --out-prefix demo
```

- Using a YouTube URL:
```
python run_pipeline.py \
  --youtube-url https://www.youtube.com/watch?v=XXXX \
  --provider Gemini --gemini-key YOUR_GEMINI_KEY \
  --min-len 25 --max-len 45 --max-clips 4 \
  --aspect 16:9 --crop-mode Center \
  --title-mode Auto \
  --out-prefix yt_demo
```

- Providing your own SRT to skip transcription:
```
python run_pipeline.py \
  --video-file path/to/long_video.mp4 \
  --srt-file path/to/subtitles.srt \
  --provider OpenAI --openai-key $OPENAI_API_KEY \
  --title-mode Custom --custom-title "My Clip" \
  --out-prefix custom
```

Tips
- You can set `OPENAI_API_KEY` or `GEMINI_API_KEY` as environment variables and omit the corresponding CLI flags.
- The CLI generates one or more MP4s plus optional per-clip SRTs, then zips them into `<out_prefix>_results.zip`.
- Face tracking requires OpenCV's Haar cascade. The code tries common locations (cv2.data.haarcascades or a local XML file). If not found or no face is detected, it falls back to center crop.

License
MIT
