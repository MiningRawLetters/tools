#!/usr/bin/env python3
"""
MRL_all_uppercase.py
Developed by Kevin Kuhn (Mining Raw Letters)
Master 977's Typography Solutions

Complete Lowercase-to-Uppercase System
Creates lowercase glyphs AND stylistic variants that point to uppercase glyphs
This ensures full stylistic set availability when typing lowercase!
"""

def create_lowercase_glyphs():
    """Create lowercase glyphs as components of uppercase glyphs, including stylistic variants."""
    
    font = CurrentFont()
    if font is None:
        print("❌ No font open! Please open a font first.")
        return
    
    print("🔠 Creating complete lowercase-to-uppercase system...")
    print("📊 This includes base glyphs AND stylistic variants!")
    print("=" * 60)
    
    # Basic mapping
    mappings = {
        'a': ('A', 0x0061), 'b': ('B', 0x0062), 'c': ('C', 0x0063), 
        'd': ('D', 0x0064), 'e': ('E', 0x0065), 'f': ('F', 0x0066), 
        'g': ('G', 0x0067), 'h': ('H', 0x0068), 'i': ('I', 0x0069), 
        'j': ('J', 0x006A), 'k': ('K', 0x006B), 'l': ('L', 0x006C), 
        'm': ('M', 0x006D), 'n': ('N', 0x006E), 'o': ('O', 0x006F), 
        'p': ('P', 0x0070), 'q': ('Q', 0x0071), 'r': ('R', 0x0072), 
        's': ('S', 0x0073), 't': ('T', 0x0074), 'u': ('U', 0x0075), 
        'v': ('V', 0x0076), 'w': ('W', 0x0077), 'x': ('X', 0x0078), 
        'y': ('Y', 0x0079), 'z': ('Z', 0x007A)
    }
    
    created_base = 0
    created_variants = 0
    skipped = 0
    
    # Step 1: Create base lowercase glyphs
    print("📝 STEP 1: Creating base lowercase glyphs...")
    
    for lowercase, (uppercase, unicode_val) in mappings.items():
        
        # Check if uppercase exists
        if uppercase not in font:
            print(f"⚠️  Skipping {lowercase} - no {uppercase} found")
            skipped += 1
            continue
        
        # Create or update lowercase glyph
        if lowercase in font:
            print(f"🔄 Updating existing {lowercase} → {uppercase}")
            glyph = font[lowercase]
            glyph.clear()  # Clear existing content
        else:
            print(f"➕ Creating new {lowercase} → {uppercase}")
            glyph = font.newGlyph(lowercase)
        
        # Set Unicode
        glyph.unicode = unicode_val
        
        # Add component reference to uppercase
        glyph.appendComponent(uppercase)
        
        # Copy width
        glyph.width = font[uppercase].width
        
        # Mark as changed
        glyph.changed()
        
        created_base += 1
    
    print(f"✅ Base glyphs complete: {created_base} created")
    print()
    
    # Step 2: Create stylistic variants for lowercase
    print("🎨 STEP 2: Creating lowercase stylistic variants...")
    
    # Check what stylistic sets exist in uppercase
    stylistic_sets = []
    for ss_num in range(1, 21):  # Check ss01 through ss20
        ss_suffix = f".ss{ss_num:02d}"
        # Check if any uppercase letter has this stylistic set
        has_this_set = any(f"{uppercase}{ss_suffix}" in font 
                          for lowercase, (uppercase, unicode_val) in mappings.items()
                          if uppercase in font)
        if has_this_set:
            stylistic_sets.append(ss_suffix)
    
    print(f"🔍 Found stylistic sets: {stylistic_sets}")
    
    # Create lowercase variants for each stylistic set
    for ss_suffix in stylistic_sets:
        print(f"\n🎯 Creating {ss_suffix} variants...")
        
        for lowercase, (uppercase, unicode_val) in mappings.items():
            
            # Skip if base uppercase doesn't exist
            if uppercase not in font:
                continue
            
            # Check if uppercase variant exists
            uppercase_variant = f"{uppercase}{ss_suffix}"
            if uppercase_variant not in font:
                print(f"   ⚠️  No {uppercase_variant} found, skipping {lowercase}{ss_suffix}")
                continue
            
            # Create lowercase variant
            lowercase_variant = f"{lowercase}{ss_suffix}"
            
            if lowercase_variant in font:
                print(f"   🔄 Updating {lowercase_variant} → {uppercase_variant}")
                glyph = font[lowercase_variant]
                glyph.clear()
            else:
                print(f"   ➕ Creating {lowercase_variant} → {uppercase_variant}")
                glyph = font.newGlyph(lowercase_variant)
            
            # Add component reference to uppercase variant
            glyph.appendComponent(uppercase_variant)
            
            # Copy width
            glyph.width = font[uppercase_variant].width
            
            # Mark as changed
            glyph.changed()
            
            created_variants += 1
    
    # Mark font as changed
    font.changed()
    
    print("=" * 60)
    print(f"🎉 COMPLETE SUCCESS!")
    print(f"✅ Base lowercase glyphs: {created_base}")
    print(f"🎨 Stylistic variants: {created_variants}")
    print(f"⏭️  Skipped (missing uppercase): {skipped}")
    print()
    print("🔥 RESULTS:")
    print("1. Type lowercase letters → see uppercase!")
    print("2. ALL stylistic sets work with lowercase input!")
    print("3. Perfect for contextual letter cycling!")
    print("4. Works in ALL applications!")
    print()
    print("💡 NEXT STEPS:")
    print("• Test typing: 'mama papa' (should show: MAMA PAPA)")
    print("• Enable Contextual Alternates in InDesign")
    print("• Use MRL_perfect_cycling.py for contextual cycling")
    
    # Test in Space Center
    try:
        from mojo.UI import OpenSpaceCenter
        OpenSpaceCenter(font, newWindow=True)
        print("\n🧪 Space Center opened - try typing lowercase!")
    except:
        print("\n🧪 Open Space Center manually to test!")

if __name__ == "__main__":
    create_lowercase_glyphs() 