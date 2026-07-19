# MRL_set_vertical_metrics.py
# Developed by Kevin Kuhn (Mining Raw Letters)

# This script sets all necessary vertical metrics for all open fonts
# to ensure consistent line spacing across different platforms and applications.

# --- Configuration ---
ASCENDER = 810
DESCENDER = -90
CAP_HEIGHT = 720
X_HEIGHT = 500
UNITS_PER_EM = 1000
# --- End Configuration ---

def set_unified_vertical_metrics(font):
    """
    Applies a consistent set of vertical metric values to a font.
    This follows the "webfont strategy" for cross-platform consistency.
    """
    print(f"Processing {font.info.familyName} {font.info.styleName}...")

    # Set basic font info values
    font.info.unitsPerEm = UNITS_PER_EM
    font.info.ascender = ASCENDER
    font.info.descender = DESCENDER
    font.info.capHeight = CAP_HEIGHT
    font.info.xHeight = X_HEIGHT

    # sTypo metrics (for modern apps)
    font.info.openTypeOS2TypoAscender = ASCENDER
    font.info.openTypeOS2TypoDescender = DESCENDER
    font.info.openTypeOS2TypoLineGap = 0

    # hhea metrics (for macOS/Linux)
    font.info.openTypeHheaAscender = ASCENDER
    font.info.openTypeHheaDescender = DESCENDER
    font.info.openTypeHheaLineGap = 0
    
    # win metrics (for Windows)
    # Note: winDescent is a positive value.
    font.info.openTypeOS2WinAscent = ASCENDER
    font.info.openTypeOS2WinDescent = abs(DESCENDER)

    # Set the 'useTypoMetrics' flag (fsSelection bit 7)
    # This tells applications to prefer the sTypo values, improving consistency.
    if font.info.openTypeOS2Selection:
        if 7 not in font.info.openTypeOS2Selection:
            font.info.openTypeOS2Selection.append(7)
    else:
        font.info.openTypeOS2Selection = [7]

    print(f" ...done.")


def main():
    """
    Main function to run the script on all open fonts.
    """
    open_fonts = AllFonts()
    if not open_fonts:
        print("No fonts open. Please open the fonts you want to modify.")
        return

    print(f"Found {len(open_fonts)} font(s) to process.")
    for font in open_fonts:
        set_unified_vertical_metrics(font)
    
    print("\nVertical metrics have been updated for all open fonts.")

if __name__ == "__main__":
    main() 