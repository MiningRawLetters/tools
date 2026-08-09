# MRL Glyph Dimensions - Test Script
# Developed by Kevin Kuhn (Mining Raw Letters)

"""
Test script for MRL Glyph Dimensions extension.
This script tests the utility functions and basic functionality.
"""

import sys
import os

# Add the lib directory to the path
lib_path = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.insert(0, lib_path)

try:
    from mrl_glyph_dimensions_utils import *
    print("✓ Successfully imported utility functions")
except ImportError as e:
    print(f"✗ Failed to import utility functions: {e}")
    sys.exit(1)

def test_preset_configurations():
    """Test preset configuration functionality."""
    print("\n--- Testing Preset Configurations ---")
    
    # Test listing presets
    presets = list_preset_configurations()
    print(f"Available presets: {presets}")
    
    # Test getting specific presets
    for preset_name in presets:
        preset = get_preset_configuration(preset_name)
        if preset:
            print(f"✓ Found preset '{preset_name}': {preset['name']}")
        else:
            print(f"✗ Failed to get preset '{preset_name}'")

def test_validation_functions():
    """Test validation functions."""
    print("\n--- Testing Validation Functions ---")
    
    # Test metric value validation
    test_values = [
        ("100", None, None, True),
        ("-50", None, None, True),
        ("abc", None, None, False),
        ("150", 100, 200, True),
        ("50", 100, 200, False),
        ("250", 100, 200, False),
    ]
    
    for value, min_val, max_val, should_pass in test_values:
        result = validate_metric_value(value, min_val, max_val)
        if should_pass and result is not None:
            print(f"✓ Validated '{value}' (min={min_val}, max={max_val}): {result}")
        elif not should_pass and result is None:
            print(f"✓ Correctly rejected '{value}' (min={min_val}, max={max_val})")
        else:
            print(f"✗ Validation failed for '{value}' (min={min_val}, max={max_val}): got {result}")

def test_font_validation():
    """Test font validation (requires RoboFont)."""
    print("\n--- Testing Font Validation ---")
    
    try:
        font = validate_current_font()
        if font:
            print(f"✓ Font validation successful: {font.info.familyName}")
            
            # Test font metrics summary
            summary = get_font_metrics_summary(font)
            if summary:
                print(f"✓ Font metrics summary: {summary['font_name']}, {summary['glyph_count']} glyphs")
            else:
                print("✗ Failed to get font metrics summary")
        else:
            print("ℹ No font currently open")
    except RuntimeError as e:
        print(f"ℹ Font validation: {e}")
    except Exception as e:
        print(f"✗ Font validation error: {e}")

def test_glyph_metrics():
    """Test glyph metrics (requires RoboFont with selected glyph)."""
    print("\n--- Testing Glyph Metrics ---")
    
    try:
        from mojo.roboFont import CurrentFont
        font = CurrentFont()
        
        if font:
            current_glyph = font.getCurrentGlyph()
            if current_glyph:
                metrics = get_glyph_metrics(current_glyph)
                if metrics:
                    print(f"✓ Glyph metrics for '{metrics['name']}':")
                    print(f"  Width: {metrics['width']}")
                    print(f"  Left margin: {metrics['left_margin']}")
                    print(f"  Right margin: {metrics['right_margin']}")
                    print(f"  Outline width: {metrics['outline_width']}")
                else:
                    print("✗ Failed to get glyph metrics")
            else:
                print("ℹ No glyph currently selected")
        else:
            print("ℹ No font currently open")
    except Exception as e:
        print(f"✗ Glyph metrics error: {e}")

def main():
    """Run all tests."""
    print("MRL Glyph Dimensions Extension - Test Suite")
    print("=" * 50)
    
    # Test utility functions
    test_preset_configurations()
    test_validation_functions()
    
    # Test RoboFont-dependent functions
    test_font_validation()
    test_glyph_metrics()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")

if __name__ == "__main__":
    main() 