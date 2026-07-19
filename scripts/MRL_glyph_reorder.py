# RoboFont Script: MRL School Pixel Glyph Reordering (CORRECTED)
# Works for all font sizes: 4x4, 5x5, 8x8, 16x16
# Based on the image specifications with orange numbers

from defcon import Font

def reorder_glyphs():
    """
    Reorder glyphs in MRL School Pixel fonts based on the image specifications.
    Orange numbers indicate WHERE each current glyph should GO:
    0 = base glyph (no suffix)
    1 = .ss01
    2 = .ss02  
    3 = .ss03
    
    Works for all font sizes (4x4, 5x5, 8x8, 16x16) with the same glyph naming.
    """
    
    # Get current font
    font = CurrentFont()
    if font is None:
        print("No font is open!")
        return
    
    # Define the reordering mapping based on the image annotations
    # Format: 'base_name': [what_becomes_base, what_becomes_ss01, what_becomes_ss02, what_becomes_ss03]
    # Based on orange numbers showing WHERE current glyphs should GO
    
    glyph_mappings = {
        # Only process D - other letters have already been reordered
        'D': ['D.ss01', 'D.ss02', 'D', 'D.ss03'],           # 2,0,1,3 -> new: [ss01, ss02, base, ss03]
    }
    
    print("Starting glyph reordering...")
    
    # Perform the reordering
    for base_name, mapping in glyph_mappings.items():
        print(f"Processing {base_name}...")
        
        # Determine how many variants this glyph has
        num_variants = len(mapping)
        if num_variants == 2:
            suffixes = ['', '.ss01']
        elif num_variants == 4:
            suffixes = ['', '.ss01', '.ss02', '.ss03']
        else:
            print(f"Unexpected number of variants for {base_name}: {num_variants}")
            continue
            
        # Check if all source glyphs exist
        source_glyphs = []
        for source_name in mapping:
            if source_name in font:
                source_glyphs.append(font[source_name])
            else:
                print(f"Warning: {source_name} not found in font!")
                source_glyphs.append(None)
        
        # Skip if any glyphs are missing
        if None in source_glyphs:
            print(f"Skipping {base_name} due to missing glyphs")
            continue
        
        # Create temporary copies to avoid conflicts
        temp_glyphs = []
        for i, glyph in enumerate(source_glyphs):
            temp_name = f"{base_name}_temp_{i}"
            temp_glyph = font.newGlyph(temp_name)
            temp_glyph.clear()
            temp_glyph.appendGlyph(glyph)
            temp_glyph.width = glyph.width
            temp_glyphs.append(temp_glyph)
        
        # Now assign the temp glyphs to their new positions
        for i, temp_glyph in enumerate(temp_glyphs):
            target_name = base_name + suffixes[i]
            if target_name in font:
                target_glyph = font[target_name]
                target_glyph.clear()
                target_glyph.appendGlyph(temp_glyph)
                target_glyph.width = temp_glyph.width
            else:
                # Create new glyph if it doesn't exist
                new_glyph = font.newGlyph(target_name)
                new_glyph.appendGlyph(temp_glyph)
                new_glyph.width = temp_glyph.width
        
        # Clean up temporary glyphs
        for temp_glyph in temp_glyphs:
            del font[temp_glyph.name]
    
    print("Glyph reordering complete!")
    print("You may need to regenerate your features if they reference specific glyph names.")

# Run the script
if __name__ == "__main__":
    reorder_glyphs() 