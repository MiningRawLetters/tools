"""
MRL Unicode Conflict Fixer
Removes Unicode assignments from stylistic alternates to prevent cmap conflicts.

This script ensures that only base glyphs have Unicode assignments,
while stylistic alternates (.ss01, .ss02, .ss03) have no Unicode assignments.
"""

import os
import xml.etree.ElementTree as ET

def fix_unicode_conflicts_in_ufo(ufo_path):
    """Remove Unicode assignments from stylistic alternates in a UFO font."""
    glyphs_dir = os.path.join(ufo_path, 'glyphs')
    
    if not os.path.exists(glyphs_dir):
        print(f"Glyphs directory not found in {ufo_path}")
        return
    
    conflicts_fixed = 0
    
    # Find all .glif files
    for filename in os.listdir(glyphs_dir):
        if not filename.endswith('.glif'):
            continue
            
        # Check if this is a stylistic alternate
        if '.ss01.glif' in filename or '.ss02.glif' in filename or '.ss03.glif' in filename:
            glif_path = os.path.join(glyphs_dir, filename)
            
            # Parse the XML
            try:
                tree = ET.parse(glif_path)
                root = tree.getroot()
                
                # Find and remove any Unicode elements
                unicode_elements = root.findall('unicode')
                if unicode_elements:
                    print(f"Removing Unicode assignments from {filename}")
                    for unicode_elem in unicode_elements:
                        root.remove(unicode_elem)
                    
                    # Write back the modified file
                    tree.write(glif_path, encoding='UTF-8', xml_declaration=True)
                    conflicts_fixed += 1
                    
            except ET.ParseError as e:
                print(f"Error parsing {filename}: {e}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return conflicts_fixed

def main():
    """Main function to fix Unicode conflicts in all MRL School Pixel fonts."""
    # Base path to the font files
    base_path = "../MRL School Pixel/fonts/250630 corrected"
    
    # UFO directories to process
    ufo_directories = [
        "250630 MRL School Pixel 4x4_NM.ufo",
        "250630 MRL School Pixel 5x5_NM.ufo", 
        "250630 MRL School Pixel 8x8_NM.ufo",
        "250630 MRL School Pixel 16x16_NM.ufo"
    ]
    
    total_fixes = 0
    
    for ufo_dir in ufo_directories:
        ufo_path = os.path.join(base_path, ufo_dir)
        
        if os.path.exists(ufo_path):
            print(f"\nProcessing {ufo_dir}...")
            fixes = fix_unicode_conflicts_in_ufo(ufo_path)
            total_fixes += fixes
            print(f"Fixed {fixes} Unicode conflicts in {ufo_dir}")
        else:
            print(f"UFO directory not found: {ufo_path}")
    
    print(f"\nTotal Unicode conflicts fixed: {total_fixes}")
    print("\nDone! You can now try generating your fonts again.")

if __name__ == "__main__":
    main() 