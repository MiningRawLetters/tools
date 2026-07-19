# MRL Fixed Gap Spacing (8x8)
# Developed by Kevin Kuhn (Mining Raw Letters)

"""
Applies a fixed sidebearing value to each side of the glyphs
in the 8x8 pixel font to create a consistent gap of 180 units between them.

Logic defined by Master 977.
"""

from mojo.roboFont import CurrentFont

# --- Configuration ---

# The fixed sidebearing to apply to each side for the 8x8 font.
# Total gap will be 90 + 90 = 180.
SIDE_MARGIN = 180
TARGET_STYLE = '4x4'

# --- Main Script ---

def main():
    """
    Main function to run the spacing conversion on the current font.
    """
    font = CurrentFont()
    if font is None:
        print("Codette: No font open. Please open a font to process.")
        return

    # This script is specifically for the 8x8 font style.
    if TARGET_STYLE not in font.info.styleName:
        print(f"Codette: This script is for the '{TARGET_STYLE}' font, but you have '{font.info.styleName}' open.")
        return

    print(f"Codette: Greetings Master 977. Applying fixed 90-unit sidebearings to {font.info.styleName}...")
    
    font.prepareUndo("Apply Fixed Gap Spacing (8x8)")
    
    glyphs_processed = 0
    for glyph in font:
        if not glyph.bounds:
            continue
            
        glyph_width = glyph.bounds[2] - glyph.bounds[0]

        glyph.leftMargin = SIDE_MARGIN
        glyph.rightMargin = SIDE_MARGIN
        glyph.width = glyph.leftMargin + glyph_width + glyph.rightMargin
        glyphs_processed += 1
    
    font.performUndo()
    font.update()

    print(f"Codette: Fixed gap spacing applied to {glyphs_processed} glyphs.")
    print(f"Codette: Mission complete for {font.info.styleName}.")

if __name__ == '__main__':
    main() 