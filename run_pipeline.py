import os
import argparse
from typing import Optional

from pipeline_advanced import generate_pipeline


class NamedPath:
    """Lightweight wrapper to mimic Gradio's uploaded file objects which expose a .name attribute."""
    def __init__(self, path: Optional[str]):
        # Accept empty/None and normalize
        self.name = path if path else ''


def parse_args():
    p = argparse.ArgumentParser(description="AI Shorts Generator - CLI runner")

    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--youtube-url", type=str, help="YouTube video URL to download and process")
    src.add_argument("--video-file", type=str, help="Local video file path to process")

    p.add_argument("--srt-file", type=str, help="Optional SRT file to skip transcription and use its timing/text")

    p.add_argument("--provider", choices=["OpenAI", "Gemini"], default="OpenAI",
                   help="LLM provider to use for highlight selection and title generation")
    p.add_argument("--openai-key", type=str, default=os.getenv("OPENAI_API_KEY", ""),
                   help="OpenAI API key (fallback to env OPENAI_API_KEY)")
    p.add_argument("--gemini-key", type=str, default=os.getenv("GEMINI_API_KEY", ""),
                   help="Gemini API key (fallback to env GEMINI_API_KEY)")

    p.add_argument("--min-len", type=float, default=15, help="Minimum clip length (seconds)")
    p.add_argument("--max-len", type=float, default=60, help="Maximum clip length (seconds)")
    p.add_argument("--max-clips", type=int, default=5, help="Maximum number of clips to generate")

    p.add_argument("--aspect", choices=["9:16", "16:9", "1:1"], default="9:16",
                   help="Target aspect ratio for output clips")
    p.add_argument("--crop-mode", choices=["Center", "Face-track"], default="Center",
                   help="Cropping mode: simple center crop or face tracking where possible")

    p.add_argument("--karaoke", action="store_true", help="Burn karaoke-style subtitles into the clips")
    p.add_argument("--export-srt", action="store_true", help="Export per-clip SRT files alongside clips")

    p.add_argument("--title-mode", choices=["Auto", "Custom", "None"], default="Auto",
                   help="How to set titles for the clips")
    p.add_argument("--custom-title", type=str, default="", help="Custom title text if --title-mode=Custom")
    p.add_argument("--platform", choices=["TikTok", "YouTube", "Instagram"], default="TikTok",
                   help="Platform to adjust title overlay layout slightly")

    p.add_argument("--watermark", type=str, help="Path to watermark/logo image to overlay")

    p.add_argument("--out-prefix", type=str, default="short", help="Prefix for output files")

    seo = p.add_mutually_exclusive_group(required=False)
    seo.add_argument("--seo-text", type=str, default="", help="Optional SEO/description text to include in zip")
    seo.add_argument("--seo-text-file", type=str, help="Path to a text file with SEO/description content")

    return p.parse_args()


def main():
    args = parse_args()

    youtube_url = args.youtube_url or None
    video_file = NamedPath(args.video_file) if args.video_file else None
    srt_file = NamedPath(args.srt_file) if args.srt_file else None
    watermark_file = NamedPath(args.watermark) if args.watermark else None

    # Load SEO text from file if provided
    seo_text = args.seo_text or ""
    if args.seo_text_file and os.path.exists(args.seo_text_file):
        try:
            with open(args.seo_text_file, "r", encoding="utf-8", errors="ignore") as f:
                seo_text = f.read()
        except Exception:
            pass

    zip_path = generate_pipeline(
        youtube_url=youtube_url,
        video_file=video_file,
        srt_file=srt_file,
        provider=args.provider,
        openai_key=args.openai_key,
        gemini_key=args.gemini_key,
        min_len=args.min_len,
        max_len=args.max_len,
        max_clips=args.max_clips,
        aspect=args.aspect,
        crop_mode=args.crop_mode,
        karaoke=args.karaoke,
        export_srt=args.export_srt,
        title_mode=args.title_mode,
        custom_title=args.custom_title,
        platform=args.platform,
        out_prefix=args.out_prefix,
        watermark_file=watermark_file,
        seo_text=seo_text,
        logger=print,
    )

    if zip_path:
        print(f"Success! Results saved to: {zip_path}")
    else:
        print("Pipeline did not produce results. Check logs above for details.")


if __name__ == "__main__":
    main()
