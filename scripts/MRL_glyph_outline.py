#!/usr/bin/env python3
"""
MRL_glyph_outline.py
Developed by Kevin Kuhn (Mining Raw Letters)
Master 977's Typography Solutions

Creates an outline around each glyph with specified spacing:
- Outer boundary: 3 units from glyph bounds
- Two outline lines with 2 units distance between them
"""

from mojo.roboFont import CurrentFont
from mojo.UI import Message, AskString
from fontParts.base import BaseGlyph
from fontParts.base.base import BaseObject
from fontTools.pens.basePen import BasePen
import math

def get_glyph_bounds(glyph):
    """Get the bounding box of a glyph, handling empty glyphs."""
    if not glyph or not glyph.bounds:
        return None
    
    bounds = glyph.bounds
    if len(bounds) != 4:
        return None
    
    return bounds  # (xMin, yMin, xMax, yMax)



def add_outline_to_glyph(glyph, outer_distance=3, line_distance=2):
    """
    Add outline contour to a glyph.
    
    Args:
        glyph: The glyph to add outline to
        outer_distance: Distance from glyph bounds to outer outline
        line_distance: Distance between the two outline lines
    
    Returns:
        bool: True if outline was added successfully
    """
    try:
        bounds = get_glyph_bounds(glyph)
        if not bounds:
            return False
        
        x_min, y_min, x_max, y_max = bounds
        
        # Calculate outline rectangle coordinates
        # Inner rectangle (3 units from glyph bounds)
        inner_left = x_min - outer_distance
        inner_right = x_max + outer_distance
        inner_bottom = y_min - outer_distance
        inner_top = y_max + outer_distance
        
        # Outer rectangle (2 units from inner line, so 5 units total from glyph bounds)
        # This creates a 2-unit space between the two lines
        outer_left = inner_left - line_distance
        outer_right = inner_right + line_distance
        outer_bottom = inner_bottom - line_distance
        outer_top = inner_top + line_distance
        
        # Create a new RGlyph to build the outline
        from mojo.roboFont import RGlyph
        outline_glyph = RGlyph()
        pen = outline_glyph.getPointPen()
        
        # Create a single contour with a hole (donut shape)
        # This creates a thin outline frame instead of filled rectangles
        pen.beginPath()
        
        # Outer rectangle (clockwise)
        pen.addPoint((outer_left, outer_bottom), "line")
        pen.addPoint((outer_right, outer_bottom), "line")
        pen.addPoint((outer_right, outer_top), "line")
        pen.addPoint((outer_left, outer_top), "line")
        pen.addPoint((outer_left, outer_bottom), "line")
        
        # Inner rectangle (counter-clockwise to create hole)
        pen.addPoint((inner_left, inner_bottom), "line")
        pen.addPoint((inner_left, inner_top), "line")
        pen.addPoint((inner_right, inner_top), "line")
        pen.addPoint((inner_right, inner_bottom), "line")
        pen.addPoint((inner_left, inner_bottom), "line")
        
        pen.endPath()
        
        # Add the outline contours to the original glyph
        for contour in outline_glyph.contours:
            glyph.appendContour(contour)
        
        # Update the glyph
        glyph.changed()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error adding outline to '{glyph.name}': {e}")
        return False

def process_font_outlines(font, outer_distance=3, line_distance=2, selected_only=False):
    """
    Process all glyphs in the font to add outlines.
    
    Args:
        font: The font to process
        outer_distance: Distance from glyph bounds to outer outline
        line_distance: Distance between the two outline lines
        selected_only: If True, only process selected glyphs
    """
    if not font:
        print("❌ No font open")
        return
    
    # Determine which glyphs to process
    if selected_only:
        glyphs_to_process = [g for g in font.selectedGlyphs if g.selected]
        if not glyphs_to_process:
            print("❌ No glyphs selected")
            Message("Please select at least one glyph first!")
            return
    else:
        glyphs_to_process = [g for g in font]
    
    print(f"=== MRL Glyph Outline Generator ===")
    print(f"Font: {getattr(font.info, 'familyName', 'Unnamed')}")
    print(f"Outer distance: {outer_distance} units")
    print(f"Line distance: {line_distance} units")
    print(f"Processing {'selected' if selected_only else 'all'} glyphs...")
    print(f"Total glyphs to process: {len(glyphs_to_process)}")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for glyph in glyphs_to_process:
        if not glyph.bounds:
            print(f"  ⏭️  Skipping '{glyph.name}' - empty glyph")
            skipped_count += 1
            continue
        
        print(f"  📝 Processing '{glyph.name}'...", end=" ")
        
        if add_outline_to_glyph(glyph, outer_distance, line_distance):
            print("✅")
            success_count += 1
        else:
            print("❌")
            error_count += 1
    
    print("-" * 50)
    print(f"✅ Successfully processed: {success_count} glyphs")
    if error_count > 0:
        print(f"❌ Errors: {error_count} glyphs")
    if skipped_count > 0:
        print(f"⏭️  Skipped: {skipped_count} glyphs")
    
    # Update font
    font.changed()
    
    Message(f"Outline generation complete!\n✅ {success_count} glyphs processed")

def main():
    """Main function to run the outline generator."""
    print("=== MRL Glyph Outline Generator ===")
    
    # Get current font
    font = CurrentFont()
    if not font:
        print("❌ No font open")
        Message("Please open a font first!")
        return
    
    # Get user preferences
    outer_input = AskString("Enter outer distance from glyph bounds (default: 3):", value="3")
    if outer_input is None:
        print("User cancelled")
        return
    
    line_input = AskString("Enter distance between outline lines (default: 2):", value="2")
    if line_input is None:
        print("User cancelled")
        return
    
    # Parse inputs
    try:
        outer_distance = int(outer_input)
        if outer_distance < 0:
            outer_distance = 3
            print(f"Invalid outer distance, using default: {outer_distance}")
    except ValueError:
        outer_distance = 3
        print(f"Invalid outer distance input, using default: {outer_distance}")
    
    try:
        line_distance = int(line_input)
        if line_distance < 0:
            line_distance = 2
            print(f"Invalid line distance, using default: {line_distance}")
    except ValueError:
        line_distance = 2
        print(f"Invalid line distance input, using default: {line_distance}")
    
    # Check if line distance is valid
    if line_distance >= outer_distance:
        print("⚠️  Warning: Line distance should be less than outer distance")
        Message("Warning: Line distance should be less than outer distance for proper outline effect!")
    
    # Ask if user wants to process selected glyphs only
    from mojo.UI import AskYesNoCancel
    result = AskYesNoCancel(
        "Process glyphs",
        "Process selected glyphs only?\n(No = process all glyphs)"
    )
    
    if result == -1:  # Cancel
        print("User cancelled")
        return
    
    selected_only = (result == 1)  # Yes = selected only, No = all glyphs
    
    # Process the font
    process_font_outlines(font, outer_distance, line_distance, selected_only)

if __name__ == "__main__":
    main() 