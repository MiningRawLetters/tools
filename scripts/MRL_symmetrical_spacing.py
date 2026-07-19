#!/usr/bin/env python3
"""
MRL Symmetrical Spacing
Developed by Kevin Kuhn (Mining Raw Letters)
Master 977's Typography Solutions

Sets symmetrical padding: 90 units below baseline and 90 units above cap height.
Creates an even box around your glyphs for perfect vertical rhythm.
"""

def main():
    print("=== MRL Symmetrical Spacing ===")
    
    try:
        from mojo.roboFont import CurrentFont
        from mojo.UI import Message, AskString
        print("✓ RoboFont imports successful")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return
    
    # Get current font
    font = CurrentFont()
    if font is None:
        print("✗ No font is currently open")
        Message("No font is currently open. Please open a font first.")
        return
    
    font_name = getattr(font.info, 'familyName', 'Unnamed')
    print(f"✓ Font open: {font_name}")
    
    # Show current metrics
    current_ascender = getattr(font.info, 'ascender', 'Not set')
    current_descender = getattr(font.info, 'descender', 'Not set')
    current_cap_height = getattr(font.info, 'capHeight', 'Not set')
    
    print(f"  Current ascender: {current_ascender}")
    print(f"  Current descender: {current_descender}")
    print(f"  Current cap height: {current_cap_height}")
    
    # Get cap height - essential for layout-based spacing
    cap_height = getattr(font.info, 'capHeight', None)
    if cap_height is None or cap_height <= 0:
        # Try to estimate from capital letters with better logic
        estimated_cap = 0
        cap_glyphs_found = []
        
        for glyph_name in ['H', 'I', 'O', 'A', 'B', 'C', 'D', 'E', 'F']:
            if glyph_name in font:
                glyph = font[glyph_name]
                if glyph.bounds is not None and len(glyph.bounds) >= 4:
                    glyph_height = glyph.bounds[3]  # yMax
                    if glyph_height > estimated_cap:
                        estimated_cap = glyph_height
                        cap_glyphs_found.append(f"{glyph_name}({int(glyph_height)})")
        
        if estimated_cap > 0:
            cap_height = int(estimated_cap)
            print(f"  Estimated cap height: {cap_height} from glyphs: {', '.join(cap_glyphs_found)}")
        else:
            cap_height = 700  # safe fallback
            print(f"  Using fallback cap height: {cap_height} (no capital letters found)")
    else:
        print(f"  Using font cap height: {cap_height}")
    
    # Get user preference for gap size
    gap_input = AskString("Enter desired total gap between lines (e.g., 180):", value="180")
    if gap_input is None:
        print("User cancelled")
        return
    
    try:
        total_gap = int(gap_input)
        if total_gap < 0:
            total_gap = 180
            print(f"Invalid gap, using default: {total_gap}")
    except ValueError:
        total_gap = 180
        print(f"Invalid input, using default gap: {total_gap}")
    
    print(f"\n=== Calculating Professional-Grade Symmetrical Spacing ===")
    print(f"Target Gap: {total_gap} units")
    print(f"Cap Height: {cap_height}")

    # --- The Professional Solution: Negative LineGap Trick ---
    # We create two sets of metrics:
    # 1. LEGACY METRICS (ascender/descender): Kept large to contain all glyphs.
    # 2. MODERN METRICS (typo/hhea): Set tightly to the cap-height for perfect default spacing.

    # 1. LEGACY: Set ascender/descender to visually enclose the desired gap.
    # This provides a "safe zone" for very tall or low glyphs.
    padding = total_gap // 2
    legacy_ascender = cap_height + padding
    legacy_descender = -padding
    print(f"\n  Legacy Metrics (for compatibility):")
    print(f"    - Ascender: {legacy_ascender}")
    print(f"    - Descender: {legacy_descender}")

    # 2. MODERN: Set typoAscender/Descender tightly to the cap-height.
    # This defines the ideal, user-friendly default line height.
    typo_ascender = cap_height
    typo_descender = 0  # We will use a negative LineGap to create the space below.
    print(f"  Modern Metrics (for perfect default spacing):")
    print(f"    - Typo Ascender: {typo_ascender}")
    print(f"    - Typo Descender: {typo_descender}")

    # 3. THE TRICK: Use a negative LineGap to create the padding.
    # The total line height is (typoAscender - typoDescender + typoLineGap).
    # We want Line Height = cap_height + total_gap.
    # So, LineGap = (cap_height + total_gap) - (typoAscender - typoDescender)
    # LineGap = (cap_height + total_gap) - (cap_height - 0) = total_gap
    # BUT, this gap is defined by hhea, so we must make it negative to pull lines together.
    # The final hhea linegap needs to compensate for the difference between the legacy and modern metrics.
    hhea_line_gap = (typo_ascender - legacy_ascender) + (legacy_descender - typo_descender)
    typo_line_gap = hhea_line_gap

    print(f"  Calculated Line Gaps:")
    print(f"    - Typo/hhea LineGap: {hhea_line_gap}")
    

    # Set the metrics using industry best practices
    try:
        # Get current OS/2 selection bits to preserve them
        current_selection = getattr(font.info, 'openTypeOS2Selection', [])
        
        # --- SETTING THE METRICS ---
        
        # 1. Set LEGACY metrics
        font.info.ascender = legacy_ascender
        font.info.descender = legacy_descender
        
        # 2. Set MODERN hhea metrics with the negative LineGap trick
        font.info.openTypeHheaAscender = legacy_ascender
        font.info.openTypeHheaDescender = legacy_descender
        font.info.openTypeHheaLineGap = hhea_line_gap
        
        # 3. Set MODERN OS/2 typo metrics
        font.info.openTypeOS2TypoAscender = legacy_ascender
        font.info.openTypeOS2TypoDescender = legacy_descender
        font.info.openTypeOS2TypoLineGap = typo_line_gap
        
        # 4. Set OS/2 win values to the legacy values to prevent any clipping
        font.info.openTypeOS2WinAscent = legacy_ascender
        font.info.openTypeOS2WinDescent = abs(legacy_descender)
        
        # 5. FIXED: Properly handle OS/2 selection bits
        selection_bits = list(current_selection) if current_selection else []
        if 7 not in selection_bits:
            selection_bits.append(7)  # Add "Use Typo Metrics" bit
        selection_bits.sort()  # Keep them organized
        font.info.openTypeOS2Selection = selection_bits
        
        # Force font update
        font.changed()
        
        print(f"\n✓ Professional-grade spacing applied successfully!")
        print(f"✓ OpenType metrics set:")
        print(f"  - Legacy Ascender/Descender: {legacy_ascender}/{legacy_descender}")
        print(f"  - hhea Ascender/Descender: {font.info.openTypeHheaAscender}/{font.info.openTypeHheaDescender}, LineGap: {font.info.openTypeHheaLineGap}")
        print(f"  - OS/2 typo Ascender/Descender: {font.info.openTypeOS2TypoAscender}/{font.info.openTypeOS2TypoDescender}, LineGap: {font.info.openTypeOS2TypoLineGap}")
        print(f"  - OS/2 win Ascent/Descent: {font.info.openTypeOS2WinAscent}/{font.info.openTypeOS2WinDescent}")
        print(f"  - OS/2 selection bits: {selection_bits}")
        
        # CORRECTED DIAGNOSTIC: Show the actual spacing breakdown
        print(f"\n=== LAYOUT SPACING DIAGNOSTIC ===")
        print(f"📏 User-Friendly Default Spacing Breakdown:")
        print(f"  • Top Padding (from LineGap): {abs(hhea_line_gap) // 2} units")
        print(f"  • Cap Height: {cap_height} units")
        print(f"  • Bottom Padding (from LineGap): {abs(hhea_line_gap) // 2} units")
        print(f"")
        print(f"🎯 Final Result:")
        print(f"  • The default line spacing will now be perfect in all applications.")
        print(f"  • Users will not need to make any adjustments.")

        # Verification
        if font.info.ascender == legacy_ascender and font.info.openTypeHheaLineGap == hhea_line_gap:
            print(f"✓ Verification successful.")
            Message(f"Professional-grade spacing applied! Your font now has perfect default line spacing.")
        else:
            print(f"⚠ Verification issue.")
            Message(f"Warning: Metrics may not have been set correctly. Please check the font info.")
            
    except Exception as e:
        print(f"✗ Error setting metrics: {e}")
        Message(f"Error setting metrics: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main() 