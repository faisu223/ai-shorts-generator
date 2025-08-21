import os
from typing import Tuple, Optional, List, Callable
import numpy as np
import cv2
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop as mp_crop


def aspect_tuple(s: str) -> Tuple[int, int]:
    a, b = s.split(':')
    return int(a), int(b)


def compute_center_crop(w: int, h: int, ratio: str) -> Tuple[int, int, int, int]:
    aw, ah = aspect_tuple(ratio)
    tr = aw / ah
    sr = w / h
    if sr > tr:
        cw = int(h * tr)
        ch = h
        x = (w - cw) // 2
        y = 0
    else:
        cw = w
        ch = int(w / tr)
        x = 0
        y = (h - ch) // 2
    return x, y, cw, ch


def crop_center(v: VideoFileClip, ratio: str) -> VideoFileClip:
    x, y, cw, ch = compute_center_crop(v.w, v.h, ratio)
    return mp_crop(v, x1=x, y1=y, width=cw, height=ch).resize((cw, ch))


# -------------- Face detection & tracking --------------
_HAAR: Optional[cv2.CascadeClassifier] = None

def _load_haar():
    global _HAAR
    if _HAAR is None:
        try:
            candidates = []
            haar_dir = getattr(cv2.data, 'haarcascades', '')
            if haar_dir:
                candidates.append(os.path.join(haar_dir, 'haarcascade_frontalface_default.xml'))
            candidates.append('haarcascade_frontalface_default.xml')
            candidates.append(os.path.join('models', 'haarcascade_frontalface_default.xml'))
            path = next((p for p in candidates if os.path.exists(p)), '')
            if path:
                _HAAR = cv2.CascadeClassifier(path)
            else:
                _HAAR = None
        except Exception:
            _HAAR = None


def detect_face(frame) -> Optional[Tuple[int, int, int, int]]:
    _load_haar()
    if _HAAR is None:
        return None
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    det = _HAAR.detectMultiScale(gray, 1.2, 3)
    if len(det) == 0:
        return None
    det = sorted(det, key=lambda d: d[2]*d[3], reverse=True)[0]
    return int(det[0]), int(det[1]), int(det[2]), int(det[3])


def crop_face_track(v: VideoFileClip, ratio: str, sample_fps: float = 4.0, smooth: float = 0.8) -> VideoFileClip:
    aw, ah = aspect_tuple(ratio)
    tr = aw / ah
    w, h = v.w, v.h
    sr = w / h
    if sr > tr:
        ch = h
        cw = int(h * tr)
    else:
        cw = w
        ch = int(w / tr)
    duration = v.duration
    times = np.arange(0, duration, 1.0/max(1.0, sample_fps))
    path: List[Tuple[float, int, int]] = []
    prev = None
    for t in times:
        try:
            frame = v.get_frame(t)
            b = detect_face(frame)
            if b:
                x, y, bw, bh = b
                cx, cy = x + bw/2, y + bh/2
            else:
                cx, cy = prev if prev else (w/2, h/2)
            if prev is None:
                sx, sy = cx, cy
            else:
                sx = smooth*prev[0] + (1-smooth)*cx
                sy = smooth*prev[1] + (1-smooth)*cy
            prev = (sx, sy)
            x1 = max(0, min(w - cw, int(sx - cw/2)))
            y1 = max(0, min(h - ch, int(sy - ch/2)))
            path.append((t, x1, y1))
        except Exception:
            continue
    if not path:
        return crop_center(v, ratio)
    ts = [p[0] for p in path]
    xs = [p[1] for p in path]
    ys = [p[2] for p in path]

    def interp(series: List[int]) -> Callable[[float], float]:
        def f(t: float) -> float:
            if t <= ts[0]:
                return float(series[0])
            if t >= ts[-1]:
                return float(series[-1])
            i = max(0, np.searchsorted(ts, t) - 1)
            t0, t1 = ts[i], ts[i+1]
            v0, v1 = series[i], series[i+1]
            if t1 == t0:
                return float(v1)
            a = (t - t0) / (t1 - t0)
            return float(v0*(1-a) + v1*a)
        return f

    fx = interp(xs)
    fy = interp(ys)
    return mp_crop(v, x1=lambda t: fx(t), y1=lambda t: fy(t), width=cw, height=ch).resize((cw, ch))
