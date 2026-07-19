#!/usr/bin/env python3
"""
MRL_uppercase_font_mapper.py
Developed by Kevin Kuhn (Mining Raw Letters)
Master 977's Typography Solutions

Maps lowercase Unicode values to uppercase glyphs for all-uppercase fonts.
Handles letters, special characters, and alternates intelligently.
"""

from typing import Optional, Dict, Set, List, Tuple
import logging
import unicodedata

try:
    from mojo.roboFont import CurrentFont
    from mojo.UI import Message, AskYesNoCancel
    from fontParts.world import RFont
except ImportError as import_error:
    logging.error(f"Required RoboFont modules not available: {import_error}")
    raise


def validate_current_font() -> Optional[RFont]:
    """Validate that a font is currently open in RoboFont."""
    try:
        current_font = CurrentFont()
        if current_font is None:
            logging.error("No font is currently open in RoboFont")
            return None
        
        logging.info(f"Working with font: {getattr(current_font.info, 'familyName', 'Unnamed')}")
        return current_font
        
    except Exception as error:
        logging.error(f"Failed to access current font: {error}")
        return None


def get_glyph_unicode_values(glyph) -> Set[int]:
    """Get all Unicode values currently assigned to a glyph."""
    unicode_values = set()
    
    try:
        if hasattr(glyph, 'unicodes') and glyph.unicodes:
            unicode_values.update(glyph.unicodes)
        elif hasattr(glyph, 'unicode') and glyph.unicode is not None:
            unicode_values.add(glyph.unicode)
    except Exception as error:
        logging.warning(f"Could not get Unicode values for glyph {glyph.name}: {error}")
    
    return unicode_values


def get_lowercase_counterpart(unicode_value: int) -> Optional[int]:
    """Get the lowercase counterpart of an uppercase Unicode character."""
    try:
        char = chr(unicode_value)
        
        if char.isupper():
            lower_char = char.lower()
            if lower_char != char:
                return ord(lower_char)
                
    except (ValueError, OverflowError):
        pass
    
    return None


def is_base_glyph(glyph_name: str) -> bool:
    """Check if a glyph is a base glyph (not an alternate)."""
    alternate_suffixes = ['.ss01', '.ss02', '.ss03', '.ss04', '.ss05', '.ss06', 
                         '.ss07', '.ss08', '.ss09', '.ss10', '.ss11', '.ss12',
                         '.ss13', '.ss14', '.ss15', '.ss16', '.ss17', '.ss18',
                         '.ss19', '.ss20', '.alt', '.swsh', '.cv01', '.cv02',
                         '.cv03', '.cv04', '.cv05', '.cv06', '.cv07', '.cv08',
                         '.cv09', '.cv10']
    
    return not any(glyph_name.endswith(suffix) for suffix in alternate_suffixes)


def get_base_glyph_name(glyph_name: str) -> str:
    """Get the base glyph name by removing alternate suffixes."""
    alternate_suffixes = ['.ss01', '.ss02', '.ss03', '.ss04', '.ss05', '.ss06', 
                         '.ss07', '.ss08', '.ss09', '.ss10', '.ss11', '.ss12',
                         '.ss13', '.ss14', '.ss15', '.ss16', '.ss17', '.ss18',
                         '.ss19', '.ss20', '.alt', '.swsh', '.cv01', '.cv02',
                         '.cv03', '.cv04', '.cv05', '.cv06', '.cv07', '.cv08',
                         '.cv09', '.cv10']
    
    for suffix in alternate_suffixes:
        if glyph_name.endswith(suffix):
            return glyph_name[:-len(suffix)]
    
    return glyph_name


def categorize_glyph(glyph_name: str, unicode_values: Set[int]) -> str:
    """Categorize a glyph based on name and Unicode values."""
    # Check for alternates first
    if not is_base_glyph(glyph_name):
        return 'alternate'
    
    # Check for special glyphs
    if glyph_name.startswith('.') or glyph_name in ['space', 'nbspace']:
        return 'special'
    
    # Analyze Unicode values
    if unicode_values:
        for unicode_val in unicode_values:
            try:
                char = chr(unicode_val)
                category = unicodedata.category(char)
                
                if category.startswith('L'):  # Letters
                    return 'letter'
                elif category.startswith('N'):  # Numbers
                    return 'number'
                elif category.startswith('P'):  # Punctuation
                    return 'punctuation'
                elif category.startswith('S'):  # Symbols
                    return 'symbol'
            except (ValueError, OverflowError):
                continue
    
    return 'unknown'


def find_mappable_glyphs(font: RFont) -> Dict[str, Tuple[Set[int], Set[int], str]]:
    """Find glyphs that can be mapped to lowercase Unicode values."""
    mappable_glyphs = {}
    base_glyph_mappings = {}  # Track base glyph mappings for alternates
    stats = {'letter': 0, 'number': 0, 'punctuation': 0, 'symbol': 0, 'alternate': 0, 'special': 0, 'unknown': 0}
    
    try:
        # First pass: process base glyphs
        for glyph_name in font.keys():
            glyph = font[glyph_name]
            
            if not glyph:
                continue
            
            current_unicodes = get_glyph_unicode_values(glyph)
            category = categorize_glyph(glyph_name, current_unicodes)
            stats[category] += 1
            
            # Only process base glyphs in first pass
            if category in ['letter', 'number', 'punctuation', 'symbol'] and is_base_glyph(glyph_name):
                new_unicodes = set()
                for current_unicode in current_unicodes:
                    lowercase_counterpart = get_lowercase_counterpart(current_unicode)
                    if lowercase_counterpart:
                        new_unicodes.add(lowercase_counterpart)
                
                if new_unicodes:
                    mappable_glyphs[glyph_name] = (current_unicodes, new_unicodes, category)
                    base_glyph_mappings[glyph_name] = new_unicodes
        
        # Second pass: handle alternates
        for glyph_name in font.keys():
            glyph = font[glyph_name]
            
            if not glyph:
                continue
            
            current_unicodes = get_glyph_unicode_values(glyph)
            category = categorize_glyph(glyph_name, current_unicodes)
            
            # Handle alternates
            if category == 'alternate':
                base_name = get_base_glyph_name(glyph_name)
                
                # If the base glyph has mappings, apply similar mappings to alternate
                if base_name in base_glyph_mappings:
                    new_unicodes = set()
                    
                    # If alternate already has some unicodes, map their lowercase counterparts
                    for current_unicode in current_unicodes:
                        lowercase_counterpart = get_lowercase_counterpart(current_unicode)
                        if lowercase_counterpart:
                            new_unicodes.add(lowercase_counterpart)
                    
                    if new_unicodes:
                        mappable_glyphs[glyph_name] = (current_unicodes, new_unicodes, category)
                        logging.info(f"Alternate '{glyph_name}' inherits mapping from base '{base_name}'")
        
        # Log statistics
        total_glyphs = sum(stats.values())
        logging.info(f"All-uppercase font analysis - Total glyphs: {total_glyphs}")
        for category, count in stats.items():
            if count > 0:
                logging.info(f"  {category.title()}: {count}")
        
        logging.info(f"Found {len(mappable_glyphs)} glyphs eligible for lowercase mapping")
        return mappable_glyphs
        
    except Exception as error:
        logging.error(f"Failed to analyze font: {error}")
        return {}


def apply_lowercase_mappings(font: RFont, mappable_glyphs: Dict[str, Tuple[Set[int], Set[int], str]]) -> Tuple[int, int]:
    """Apply lowercase Unicode mappings to uppercase glyphs."""
    successful_count = 0
    failed_count = 0
    
    try:
        for glyph_name, (current_unicodes, new_unicodes, category) in mappable_glyphs.items():
            try:
                glyph = font[glyph_name]
                all_unicodes = current_unicodes | new_unicodes
                glyph.unicodes = list(all_unicodes)
                
                current_chars = [chr(u) for u in sorted(current_unicodes) if u < 0x10000]
                new_chars = [chr(u) for u in sorted(new_unicodes) if u < 0x10000]
                
                logging.info(f"Updated '{glyph_name}' ({category}): {'/'.join(current_chars)} + {'/'.join(new_chars)}")
                successful_count += 1
                
            except Exception as glyph_error:
                logging.error(f"Failed to update '{glyph_name}': {glyph_error}")
                failed_count += 1
        
        return successful_count, failed_count
        
    except Exception as error:
        logging.error(f"Failed to apply mappings: {error}")
        return 0, len(mappable_glyphs)


def main() -> None:
    """Main execution function for MRL Uppercase Font Mapper."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        font = validate_current_font()
        if font is None:
            Message("No font is currently open. Please open a font and try again.")
            return
        
        logging.info("Analyzing all-uppercase font for lowercase mapping...")
        mappable_glyphs = find_mappable_glyphs(font)
        
        if not mappable_glyphs:
            Message("No uppercase glyphs found that need lowercase mapping. Your font may already be complete!")
            return
        
        total_mappings = sum(len(new_unicodes) for _, (_, new_unicodes, _) in mappable_glyphs.items())
        
        # Show confirmation dialog
        preview = f"Found {len(mappable_glyphs)} uppercase glyphs that can accept lowercase input.\n"
        preview += f"Will add {total_mappings} lowercase Unicode mappings.\n\n"
        preview += "This will allow both uppercase AND lowercase typing to work!\n\n"
        preview += "Example mappings:\n"
        
        # Show examples by category
        categories_shown = set()
        for glyph_name, (current, new, category) in list(mappable_glyphs.items())[:8]:
            if category not in categories_shown or len(categories_shown) < 3:
                current_chars = [chr(u) for u in sorted(current) if u < 0x10000]
                new_chars = [chr(u) for u in sorted(new) if u < 0x10000]
                preview += f"  {glyph_name} ({category}): {'/'.join(current_chars)} + {'/'.join(new_chars)}\n"
                categories_shown.add(category)
        
        preview += f"\nResult: Both 'A' and 'a' will show the same uppercase glyph!"
        
        user_choice = AskYesNoCancel("Uppercase Font Mapping", preview + "\n\nProceed?")
        
        if user_choice != 1:
            logging.info("User cancelled mapping")
            return
        
        logging.info("Applying lowercase Unicode mappings to uppercase glyphs...")
        successful_count, failed_count = apply_lowercase_mappings(font, mappable_glyphs)
        
        if successful_count > 0:
            Message(f"Success! Added {total_mappings} lowercase mappings to {successful_count} glyphs.\n\nYour all-uppercase font now responds to both uppercase AND lowercase typing!\n\nAlternates are also mapped correctly.")
            logging.info("MRL Uppercase Font Mapper completed successfully")
        else:
            Message("Completed with errors. Check output window for details.")
            
    except Exception as error:
        logging.error(f"Unexpected error: {error}")
        Message(f"An error occurred: {error}")


if __name__ == "__main__":
    main() 