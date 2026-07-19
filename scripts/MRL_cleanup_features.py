#!/usr/bin/env python3
"""
MRL_cleanup_features.py
Developed by Kevin Kuhn (Mining Raw Letters)
Master 977's Typography Solutions

Find and remove broken glyph references in OpenType features.
"""

import re
from mojo.roboFont import CurrentFont
from mojo.UI import Message, AskYesNoCancel

def find_missing_glyph_references(font):
    """Find all glyph references in features that don't exist in the font."""
    if not font or not hasattr(font, 'features') or not font.features:
        return []
    
    # Get all glyph names that exist in the font
    existing_glyphs = set(font.keys())
    
    # Get the features code
    features_text = font.features.text or ""
    
    # Find all glyph references in features
    # This regex finds glyph names (letters, numbers, dots, underscores)
    glyph_pattern = r'\b[a-zA-Z][a-zA-Z0-9._]*\b'
    potential_glyphs = re.findall(glyph_pattern, features_text)
    
    # Filter to find missing ones
    missing_references = []
    feature_keywords = {
        'feature', 'sub', 'by', 'from', 'lookup', 'languagesystem',
        'script', 'language', 'pos', 'anchor', 'markClass', 'table',
        'GDEF', 'GSUB', 'GPOS', 'BASE', 'head', 'hhea', 'OS_2', 'vhea',
        'kern', 'vmtx', 'hmtx', 'post', 'name', 'include', 'exclude'
    }
    
    for glyph_name in set(potential_glyphs):
        # Skip OpenType keywords
        if glyph_name.lower() in feature_keywords:
            continue
        
        # Skip if it looks like a keyword or value
        if glyph_name.isdigit() or len(glyph_name) < 2:
            continue
            
        # Check if this glyph reference is missing from font
        if glyph_name not in existing_glyphs:
            # Find line numbers where this glyph appears
            lines = features_text.split('\n')
            line_numbers = []
            for i, line in enumerate(lines, 1):
                if glyph_name in line:
                    line_numbers.append((i, line.strip()))
            
            missing_references.append({
                'glyph': glyph_name,
                'lines': line_numbers
            })
    
    return missing_references

def cleanup_features():
    """Find and optionally remove broken glyph references."""
    font = CurrentFont()
    if not font:
        Message("Please open a font first!")
        return
    
    print("Analyzing OpenType features for broken glyph references...")
    
    missing_refs = find_missing_glyph_references(font)
    
    if not missing_refs:
        print("✅ No missing glyph references found in features!")
        Message("✅ Your OpenType features are clean!")
        return
    
    print(f"❌ Found {len(missing_refs)} missing glyph references:")
    print("=" * 60)
    
    for ref in missing_refs:
        glyph_name = ref['glyph']
        print(f"\n🚨 Missing glyph: '{glyph_name}'")
        print(f"   Found in {len(ref['lines'])} locations:")
        
        for line_num, line_text in ref['lines']:
            print(f"   Line {line_num}: {line_text}")
    
    print("\n" + "=" * 60)
    print("\n💡 SOLUTIONS:")
    print("1. Open Font → Features and manually remove these references")
    print("2. Or create the missing glyphs")
    print("3. Or use 'Clean up broken references' option below")
    
    # Ask if user wants to automatically clean up
    result = AskYesNoCancel(
        f"Found {len(missing_refs)} broken glyph references in features.",
        "Would you like to automatically remove lines containing these references?"
    )
    
    if result == 1:  # Yes
        # Auto-cleanup
        features_text = font.features.text or ""
        lines = features_text.split('\n')
        cleaned_lines = []
        removed_count = 0
        
        for line in lines:
            should_remove = False
            for ref in missing_refs:
                if ref['glyph'] in line:
                    should_remove = True
                    break
            
            if should_remove:
                print(f"🗑️  Removing line: {line.strip()}")
                removed_count += 1
            else:
                cleaned_lines.append(line)
        
        # Update features
        font.features.text = '\n'.join(cleaned_lines)
        
        print(f"\n✅ Removed {removed_count} lines with broken references")
        Message(f"✅ Cleaned up {removed_count} lines! Try exporting again.")
    
    elif result == 0:  # No
        print("Manual cleanup required. Check the lines listed above.")
        Message("Manual cleanup required. Check the output window for details.")

if __name__ == "__main__":
    cleanup_features() 