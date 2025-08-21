#!/usr/bin/env python3
"""
Error Testing Script for AI Shorts Generator
Tests various error conditions across all modules
"""

import os
import sys
import tempfile
import json
from pathlib import Path

def test_pipeline_advanced_errors():
    """Test errors in pipeline_advanced.py"""
    print("=== Testing pipeline_advanced.py ===")

    # Test 1: Invalid YouTube URL
    try:
        from pipeline_advanced import download_youtube
        result = download_youtube("https://invalid-url")
        print("❌ Error 1: Should have failed with invalid URL")
    except Exception as e:
        print(f"✅ Error 1 triggered: {type(e).__name__}: {e}")

    # Test 2: Missing video file
    try:
        from pipeline_advanced import transcribe
        result = transcribe("nonexistent_video.mp4")
        print("❌ Error 2: Should have failed with missing file")
    except Exception as e:
        print(f"✅ Error 2 triggered: {type(e).__name__}: {e}")

    # Test 3: Invalid video file (empty file)
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            empty_file = f.name
        from pipeline_advanced import transcribe
        result = transcribe(empty_file)
        print("❌ Error 3: Should have failed with empty file")
    except Exception as e:
        print(f"✅ Error 3 triggered: {type(e).__name__}: {e}")
    finally:
        if 'empty_file' in locals():
            os.unlink(empty_file)

def test_llm_utils_errors():
    """Test errors in llm_utils.py"""
    print("\n=== Testing llm_utils.py ===")

    # Test 4: Invalid API key
    try:
        from llm_utils import pick_highlights
        result = pick_highlights("test text", "OpenAI", "invalid-key", 3, 15, 60)
        print("❌ Error 4: Should have failed with invalid API key")
    except Exception as e:
        print(f"✅ Error 4 triggered: {type(e).__name__}: {e}")

    # Test 5: Empty transcription
    try:
        from llm_utils import pick_highlights
        result = pick_highlights("", "OpenAI", "sk-test", 3, 15, 60)
        print("❌ Error 5: Should have failed with empty transcription")
    except Exception as e:
        print(f"✅ Error 5 triggered: {type(e).__name__}: {e}")

    # Test 6: Invalid provider
    try:
        from llm_utils import pick_highlights
        result = pick_highlights("test", "InvalidProvider", "sk-test", 3, 15, 60)
        print("❌ Error 6: Should have failed with invalid provider")
    except Exception as e:
        print(f"✅ Error 6 triggered: {type(e).__name__}: {e}")

def test_video_utils_errors():
    """Test errors in video_utils.py"""
    print("\n=== Testing video_utils.py ===")

    # Test 7: Invalid aspect ratio format
    try:
        from video_utils import aspect_tuple
        result = aspect_tuple("16:9:1")  # Too many parts
        print("❌ Error 7: Should have failed with invalid ratio format")
    except Exception as e:
        print(f"✅ Error 7 triggered: {type(e).__name__}: {e}")

    # Test 8: Invalid aspect ratio (non-numeric)
    try:
        from video_utils import aspect_tuple
        result = aspect_tuple("abc:def")
        print("❌ Error 8: Should have failed with non-numeric ratio")
    except Exception as e:
        print(f"✅ Error 8 triggered: {type(e).__name__}: {e}")

    # Test 9: Invalid crop dimensions (zero values)
    try:
        from video_utils import compute_center_crop
        result = compute_center_crop(0, 0, "9:16")
        print("❌ Error 9: Should have failed with zero dimensions")
    except Exception as e:
        print(f"✅ Error 9 triggered: {type(e).__name__}: {e}")

def test_subs_utils_errors():
    """Test errors in subs_utils.py"""
    print("\n=== Testing subs_utils.py ===")

    # Test 10: Invalid SRT file format
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            f.write("99:99:99 --> 00:00:05\nInvalid timestamp\n")
            malformed_srt = f.name

        from subs_utils import parse_srt_segments
        result = parse_srt_segments(malformed_srt)
        print("❌ Error 10: Should have failed with malformed SRT")
    except Exception as e:
        print(f"✅ Error 10 triggered: {type(e).__name__}: {e}")
    finally:
        if 'malformed_srt' in locals():
            os.unlink(malformed_srt)

def test_run_pipeline_errors():
    """Test errors in run_pipeline.py"""
    print("\n=== Testing run_pipeline.py ===")

    # Test 11: Missing required arguments
    try:
        from run_pipeline import main
        # Simulate command line args with missing video source
        sys.argv = ['run_pipeline.py', '--min-len', '15']
        main()
        print("❌ Error 11: Should have failed with missing arguments")
    except SystemExit as e:
        print(f"✅ Error 11 triggered: SystemExit with code {e.code}")
    except Exception as e:
        print(f"✅ Error 11 triggered: {type(e).__name__}: {e}")

def test_test_imports_errors():
    """Test errors in test_imports.py"""
    print("\n=== Testing test_imports.py ===")

    # Test 12: Import non-existent module
    try:
        from test_imports import test_import
        test_import("nonexistent_module_xyz123")
        print("❌ Error 12: Should have failed importing non-existent module")
    except Exception as e:
        print(f"✅ Error 12 triggered: {type(e).__name__}: {e}")

    # Test 13: Test non-existent function
    try:
        from test_imports import test_function
        test_function("os", "nonexistent_function_xyz")
        print("❌ Error 13: Should have failed testing non-existent function")
    except Exception as e:
        print(f"✅ Error 13 triggered: {type(e).__name__}: {e}")

def test_demo_errors():
    """Test errors in demo.py"""
    print("\n=== Testing demo.py ===")

    # Test 14: Call demo_help with wrong arguments
    try:
        from demo import demo_help
        result = demo_help("invalid_arg")  # Function expects no arguments
        print("❌ Error 14: Should have failed with wrong arguments")
    except Exception as e:
        print(f"✅ Error 14 triggered: {type(e).__name__}: {e}")

def test_missing_dependencies():
    """Test missing dependency errors"""
    print("\n=== Testing missing dependencies ===")

    # Test 15: Try to use pipeline without dependencies
    try:
        # Temporarily remove path to simulate missing modules
        original_path = sys.path.copy()
        sys.path.clear()

        from pipeline_advanced import generate_pipeline
        result = generate_pipeline(None, None, None, "OpenAI", "", "", 15, 60, 3, "9:16", "Center", False, False, "None", "", "TikTok", "test", None)
        print("❌ Error 15: Should have failed without dependencies")
    except Exception as e:
        print(f"✅ Error 15 triggered: {type(e).__name__}: {e}")
    finally:
        sys.path = original_path

def main():
    """Run all error tests"""
    print("🔥 Starting Error Testing for AI Shorts Generator")
    print("=" * 60)

    test_pipeline_advanced_errors()
    test_llm_utils_errors()
    test_video_utils_errors()
    test_subs_utils_errors()
    test_run_pipeline_errors()
    test_test_imports_errors()
    test_demo_errors()
    test_missing_dependencies()

    print("\n" + "=" * 60)
    print("🎯 Error testing complete!")
    print("Check the results above for triggered errors.")

if __name__ == "__main__":
    main()
