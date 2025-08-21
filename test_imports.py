#!/usr/bin/env python3
"""
Test script to verify all imports and functions work correctly
"""

import sys
import os

def test_import(module_name):
    """Test importing a module and return status"""
    try:
        __import__(module_name)
        return True, None
    except ImportError as e:
        return False, str(e)

def test_function(module_name, function_name):
    """Test if a function exists in a module"""
    try:
        module = __import__(module_name)
        if hasattr(module, function_name):
            return True, None
        else:
            return False, f"Function '{function_name}' not found in module '{module_name}'"
    except ImportError as e:
        return False, str(e)

def main():
    print("=== AI Shorts Generator Import Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()

    # Test basic imports
    basic_imports = [
        'os', 'sys', 'typing', 'json', 'subprocess', 'shlex',
        're', 'zipfile', 'numpy', 'cv2', 'moviepy', 'gradio'
    ]

    print("=== Testing Basic Imports ===")
    for module in basic_imports:
        success, error = test_import(module)
        status = "✓" if success else "✗"
        print(f"{status} {module}: {'OK' if success else error}")

    print("\n=== Testing Project Modules ===")
    project_modules = ['llm_utils', 'subs_utils', 'video_utils', 'pipeline_advanced']

    for module in project_modules:
        success, error = test_import(module)
        status = "✓" if success else "✗"
        print(f"{status} {module}: {'OK' if success else error}")

    print("\n=== Testing Key Functions ===")
    functions_to_test = [
        ('llm_utils', 'pick_highlights'),
        ('llm_utils', 'generate_titles_from_highlights'),
        ('subs_utils', 'parse_srt_segments'),
        ('subs_utils', 'write_ass_karaoke'),
        ('video_utils', 'crop_center'),
        ('video_utils', 'crop_face_track'),
        ('pipeline_advanced', 'generate_pipeline')
    ]

    for module, func in functions_to_test:
        success, error = test_function(module, func)
        status = "✓" if success else "✗"
        print(f"{status} {module}.{func}: {'OK' if success else error}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
