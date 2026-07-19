#!/usr/bin/env python3
"""
RoboFont Script: Set Glyph Dimensions
Reduces left and right sidebearings by 90 units each while preserving vertical metrics.
"""

def set_glyph_dimensions():
    """Reduce left and right sidebearings by 90 units each, preserving vertical metrics."""
    
    # Get the current font
    from mojo.roboFont import CurrentFont
    font = CurrentFont()
    
    if not font:
        print("No font open. Please open a font first.")
        return
    
    print(f"Processing font: {font.info.familyName} {font.info.styleName}")
    print(f"Total glyphs: {len(font)}")
    
    # Counter for processed glyphs
    processed_count = 0
    skipped_count = 0
    
    # Process each glyph
    for glyph_name in font.keys():
        glyph = font[glyph_name]
        
        # Skip empty glyphs or special glyphs
        if not glyph.bounds or glyph_name.startswith('.'):
            skipped_count += 1
            continue
        
        # Get current sidebearings
        current_left_sb = glyph.leftMargin
        current_right_sb = glyph.rightMargin
        
        # Calculate new sidebearings (reduce by 90 each)
        new_left_sb = max(0, current_left_sb - 90)  # Don't go below 0
        new_right_sb = max(0, current_right_sb - 90)  # Don't go below 0
        
        # Calculate how much to shift the glyph
        left_shift = current_left_sb - new_left_sb
        right_shift = current_right_sb - new_right_sb
        
        # Move the glyph to account for the reduced sidebearings
        # We need to shift left by the amount we reduced the left sidebearing
        glyph.move((left_shift, 0))
        
        # Set the new sidebearings
        glyph.leftMargin = new_left_sb
        glyph.rightMargin = new_right_sb
        
        # Update the glyph
        glyph.update()
        
        processed_count += 1
        
        # Print progress for every 50 glyphs
        if processed_count % 50 == 0:
            print(f"Processed {processed_count} glyphs...")
    
    # Mark the font as changed
    font.changed()
    
    print(f"\nCompleted!")
    print(f"Processed: {processed_count} glyphs")
    print(f"Skipped: {skipped_count} glyphs")
    print(f"All glyphs now have reduced sidebearings by 90 units each")
    print(f"Vertical metrics (cap height, baseline, descender) preserved")

if __name__ == "__main__":
    set_glyph_dimensions() 