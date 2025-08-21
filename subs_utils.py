import re
import subprocess, shlex
from typing import List, Dict, Tuple

# ---------- SRT / Text ----------

def parse_srt_segments(path: str) -> List[Dict]:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    blocks = re.split(r'\n\s*\n', content.strip())
    segs: List[Dict] = []
    for b in blocks:
        lines = [l.strip('\ufeff ') for l in b.splitlines() if l.strip()]
        if not lines:
            continue
        time_line = None
        for l in lines:
            if '-->' in l:
                time_line = l
                break
        if not time_line:
            continue
        try:
            t0, t1 = [x.strip() for x in time_line.split('-->')]
            def to_s(ts: str) -> float:
                h, m, rest = ts.split(':')
                s, ms = (rest + ',0').split(',')[:2]
                return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
            st, et = to_s(t0), to_s(t1)
            if et > st:
                text = ' '.join([l for l in lines if l != time_line and not l.isdigit()])
                segs.append({'start': st, 'end': et, 'text': text})
        except Exception:
            pass
    return segs


def segs_to_text(segs: List[Dict]) -> str:
    return ' '.join(s.get('text', '').strip() for s in segs)


def words_from_segs(segs: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    for s in segs:
        if s.get('words'):
            out.append(s)
            continue
        text = s.get('text', '').strip()
        words = re.findall(r"\w+['’\-]?\w*|\S", text)
        dur = max(0.001, s['end'] - s['start'])
        n = max(1, len(words))
        step = dur / n
        wlist = []
        for i, w in enumerate(words):
            ws = s['start'] + i*step
            we = min(s['end'], ws + step)
            wlist.append({'start': ws, 'end': we, 'text': w})
        s2 = dict(s)
        s2['words'] = wlist
        out.append(s2)
    return out


def _srt_ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt_for_range(segs: List[Dict], path: str, t0: float, t1: float) -> None:
    """Write a simple SRT for the time range [t0, t1] using provided segments.
    Times inside the SRT start at 00:00:00,000.
    """
    idx = 1
    lines = []
    for s in segs:
        if s['end'] <= t0 or s['start'] >= t1:
            continue
        a = max(t0, s['start'])
        b = min(t1, s['end'])
        text = s.get('text', '').strip()
        if not text:
            continue
        sa = _srt_ts(a - t0)
        sb = _srt_ts(b - t0)
        lines.append(f"{idx}\n{sa} --> {sb}\n{text}\n\n")
        idx += 1
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# ---------- ASS Karaoke ----------

def _ass_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    cs = int((t - int(t)) * 100)
    return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"


def write_ass_karaoke(segs: List[Dict], path: str, t0: float, t1: float, resolution: Tuple[int, int]) -> None:
    W, H = resolution
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {W}\n"
        f"PlayResY: {H}\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Karaoke,Arial,60,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,80,80,140,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    lines = [header]
    for s in segs:
        if s['end'] < t0 or s['start'] > t1:
            continue
        a = max(t0, s['start'])
        b = min(t1, s['end'])
        words = [w for w in s.get('words', []) if not (w['end'] < a or w['start'] > b)]
        if not words:
            continue
        parts = []
        for w in words:
            ws = max(a, w['start'])
            we = min(b, w['end'])
            k = max(1, int((we - ws) * 100))
            txt = re.sub(r'[{}\\\\]', '', w['text'])
            parts.append(f"{{\\k{k}}}{txt}")
        text = ''.join(parts)
        lines.append(
            f"Dialogue: 0,{_ass_ts(a-t0)},{_ass_ts(b-t0)},Karaoke,,0000,0000,0000,,{text}\n"
        )
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def burn_ass_to_video(input_path: str, ass_path: str, output_path: str) -> None:
    cmd = f"ffmpeg -y -i {shlex.quote(input_path)} -vf subtitles={shlex.quote(ass_path)} -c:a aac -c:v libx264 -pix_fmt yuv420p {shlex.quote(output_path)}"
    subprocess.run(cmd, shell=True, check=True)
