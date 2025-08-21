#!/usr/bin/env python3
"""
Demo script showing the AI Shorts Generator functionality
"""

import os
import sys
from run_pipeline import parse_args, main

def demo_help():
    """Show demo help"""
    print("=== AI Shorts Generator Demo ===")
    print()
    print("This project is now working correctly!")
    print()
    print("Available components:")
    print("1. CLI Interface: python run_pipeline.py --help")
    print("2. Import Test: python test_imports.py")
    print("3. Pipeline Test: python test_pipeline.py")
    print()
    print("To run the full pipeline, you need:")
    print("- A video file or YouTube URL")
    print("- API keys for OpenAI or Gemini")
    print("- FFmpeg installed")
    print()
    print("Example CLI usage:")
    print("python run_pipeline.py --video-file your_video.mp4 --provider OpenAI --openai-key YOUR_KEY --min-len 15 --max-len 60 --max-clips 3 --aspect 9:16")
    print()
    print("For Colab usage, open one of the .ipynb files in Google Colab.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        demo_help()
    else:
        print("AI Shorts Generator is ready!")
        print("Run 'python demo.py --help' for more information.")
        print("Or run 'python run_pipeline.py --help' to see CLI options.")
