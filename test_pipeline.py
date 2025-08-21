#!/usr/bin/env python3
"""
Test script to verify the AI Shorts Generator pipeline works correctly
"""

import os
import sys
from pipeline_advanced import generate_pipeline

def test_pipeline():
    """Test the pipeline with dummy parameters"""
    print("=== Testing AI Shorts Generator Pipeline ===")

    # Test parameters (without actual API keys for safety)
    test_params = {
        'youtube_url': None,
        'video_file': None,
        'srt_file': None,
        'provider': 'OpenAI',
        'openai_key': 'test_key',  # Won't work but tests import
        'gemini_key': 'test_key',
        'min_len': 15,
        'max_len': 60,
        'max_clips': 1,
        'aspect': '9:16',
        'crop_mode': 'Center',
        'karaoke': False,
        'export_srt': False,
        'title_mode': 'None',
        'custom_title': '',
        'platform': 'TikTok',
        'out_prefix': 'test',
        'watermark_file': None,
        'seo_text': 'Test description',
        'logger': print
    }

    try:
        # This should fail gracefully due to missing video file
        result = generate_pipeline(**test_params)
        if result is None:
            print("✓ Pipeline correctly handled missing video file")
        else:
            print("✗ Pipeline should have returned None for missing video")
    except Exception as e:
        print(f"✗ Pipeline failed with error: {e}")

    print("\n=== Pipeline Test Complete ===")

if __name__ == "__main__":
    test_pipeline()
