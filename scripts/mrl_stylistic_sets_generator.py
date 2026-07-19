#!/usr/bin/env python3
"""
MRL Stylistic Sets Auto-Generator
Developed by Kevin Kuhn (Mining Raw Letters)
Master 977's Typography Solutions

A RoboFont script that automatically:
1. Scans font for .ss01, .ss02, etc. alternate glyphs
2. Generates OpenType features code
3. Applies features to the font
4. Ready for export!

Enhanced for special characters (underscore, ampersand, etc.) in uppercase-only typefaces.
Follows functional/declarative programming paradigm with proper error handling.
"""

import re
from typing import Optional, Dict, List, Tuple, Set
from collections import defaultdict
import logging

# RoboFont and FontParts imports
try:
    from mojo.roboFont import CurrentFont
    from mojo.UI import Message
    from defcon import Font
    from fontParts.world import RFont
except ImportError as import_error:
    logging.error(f"Required RoboFont modules not available: {import_error}")
    raise


# Special characters that should be included in stylistic sets
SPECIAL_CHARACTERS = {
    'underscore', 'ampersand', 'at', 'numbersign', 'dollar', 'percent', 
    'asciicircum', 'asterisk', 'plus', 'minus', 'equal', 'backslash',
    'bar', 'asciitilde', 'grave', 'exclamation', 'question',
    'period', 'comma', 'colon', 'semicolon', 'quotesingle', 'quotedbl'
}


def validate_current_font() -> Optional[RFont]:
    """
    Validate that a font is currently open in RoboFont.
    
    Returns:
        RFont object if valid, None if no font is open
    """
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


def extract_stylistic_set_number(glyph_name: str) -> Optional[int]:
    """
    Extract stylistic set number from glyph name.
    
    Args:
        glyph_name: Name of the glyph to analyze
        
    Returns:
        Stylistic set number if found, None otherwise
    """
    # Pattern matches: .ss01, .ss02, .ss10, etc.
    pattern = r'\.ss(\d{2})$'
    match = re.search(pattern, glyph_name)
    
    if match:
        return int(match.group(1))
    return None


def get_base_glyph_name(glyph_name: str) -> str:
    """
    Get base glyph name by removing stylistic set suffix.
    
    Args:
        glyph_name: Full glyph name with suffix
        
    Returns:
        Base glyph name without suffix
    """
    # Remove .ss## suffix
    pattern = r'\.ss\d{2}$'
    return re.sub(pattern, '', glyph_name)


def is_special_character(glyph_name: str) -> bool:
    """
    Check if glyph is a special character that should be included.
    
    Args:
        glyph_name: Base glyph name to check
        
    Returns:
        True if it's a special character, False otherwise
    """
    return glyph_name.lower() in SPECIAL_CHARACTERS


def get_proper_glyph_sort_key(glyph_name: str) -> Tuple[str, int]:
    """
    Generate proper sort key for glyph ordering in InDesign.
    This ensures base glyphs come first, then alternates in order.
    
    Args:
        glyph_name: Name of the glyph
        
    Returns:
        Tuple of (base_name, sort_order) for proper sorting
    """
    set_number = extract_stylistic_set_number(glyph_name)
    
    if set_number is None:
        # Base glyph - should come first
        return (glyph_name.lower(), 0)
    else:
        # Alternate glyph - sort by set number
        base_name = get_base_glyph_name(glyph_name)
        return (base_name.lower(), set_number)


def should_include_glyph(glyph_name: str, glyph) -> bool:
    """
    Determine if glyph should be included in stylistic sets.
    Enhanced to specifically handle special characters.
    
    Args:
        glyph_name: Name of the glyph
        glyph: Glyph object to check
        
    Returns:
        True if glyph should be included, False otherwise
    """
    if not glyph_name or not glyph:
        return False
    
    # Must have stylistic set suffix
    if extract_stylistic_set_number(glyph_name) is None:
        return False
    
    # Get base name to check
    base_name = get_base_glyph_name(glyph_name)
    
    # Log special characters for debugging
    if is_special_character(base_name):
        logging.info(f"Found special character alternate: {base_name} → {glyph_name}")
    
    # Glyph should have outlines or components
    if not hasattr(glyph, 'components') and not hasattr(glyph, 'contours'):
        return False
    
    # Skip if glyph is completely empty
    try:
        if len(glyph) == 0:
            logging.debug(f"Skipping empty glyph: {glyph_name}")
            return False
    except (AttributeError, TypeError):
        pass
    
    return True


def scan_font_for_stylistic_sets(font: RFont) -> Dict[int, List[Tuple[str, str]]]:
    """
    Scan font for stylistic set alternate glyphs.
    Enhanced to track special characters separately.
    
    Args:
        font: Font to scan
        
    Returns:
        Dictionary mapping set numbers to list of (base_name, alt_name) tuples
    """
    if font is None:
        logging.error("Font is None, cannot scan")
        return {}
    
    stylistic_sets = defaultdict(list)
    processed_count = 0
    special_char_count = 0
    
    try:
        for glyph_name in font.keys():
            glyph = font[glyph_name]
            
            if not should_include_glyph(glyph_name, glyph):
                continue
            
            set_number = extract_stylistic_set_number(glyph_name)
            if set_number is None:
                continue
            
            base_name = get_base_glyph_name(glyph_name)
            
            # Verify base glyph exists
            if base_name not in font:
                logging.warning(f"Base glyph '{base_name}' not found for alternate '{glyph_name}'")
                continue
            
            # Track special characters
            if is_special_character(base_name):
                special_char_count += 1
                logging.info(f"Added special character: {base_name} → {glyph_name} (ss{set_number:02d})")
            
            stylistic_sets[set_number].append((base_name, glyph_name))
            processed_count += 1
            
            logging.debug(f"Found: {base_name} → {glyph_name} (ss{set_number:02d})")
    
    except Exception as error:
        logging.error(f"Error scanning font for stylistic sets: {error}")
        return {}
    
    logging.info(f"Scanned font: found {processed_count} stylistic alternates ({special_char_count} special characters) in {len(stylistic_sets)} sets")
    return dict(stylistic_sets)


def generate_feature_code(stylistic_sets: Dict[int, List[Tuple[str, str]]]) -> str:
    """
    Generate OpenType features code from stylistic sets data.
    Enhanced with special character comments and proper ordering for InDesign.
    
    Args:
        stylistic_sets: Dictionary mapping set numbers to substitution pairs
        
    Returns:
        Complete OpenType features code as string
    """
    if not stylistic_sets:
        logging.warning("No stylistic sets found, generating empty features")
        return ""
    
    feature_lines = []
    feature_lines.append("# Auto-generated stylistic sets by MRL Stylistic Sets Generator")
    feature_lines.append("# Generated from existing alternate glyphs")
    feature_lines.append("# Includes special characters (underscore, ampersand, etc.)")
    feature_lines.append("# Ordered for proper display in InDesign and other applications")
    feature_lines.append("")
    
    # Generate lookups first for better InDesign ordering
    lookup_definitions = []
    
    # Sort by set number for consistent output
    for set_number in sorted(stylistic_sets.keys()):
        substitutions = stylistic_sets[set_number]
        
        if not substitutions:
            continue
        
        # Create lookup for this stylistic set
        lookup_name = f"ss{set_number:02d}_lookup"
        lookup_definitions.append(f"lookup {lookup_name} {{")
        lookup_definitions.append(f"    # Stylistic Set {set_number:02d} substitutions")
        
        # Separate letters and special characters for proper ordering
        letters = [s for s in substitutions if not is_special_character(s[0])]
        specials = [s for s in substitutions if is_special_character(s[0])]
        
        # Sort letters alphabetically by base name for consistent ordering
        sorted_letters = sorted(letters, key=lambda x: get_proper_glyph_sort_key(x[1]))
        sorted_specials = sorted(specials, key=lambda x: get_proper_glyph_sort_key(x[1]))
        
        # Generate substitutions in proper order for InDesign consistency
        all_substitutions = sorted_letters + sorted_specials
        
        for base_name, alt_name in all_substitutions:
            lookup_definitions.append(f"    sub {base_name} by {alt_name};")
        
        lookup_definitions.append(f"}} {lookup_name};")
        lookup_definitions.append("")
    
    # Add lookup definitions to feature code
    feature_lines.extend(lookup_definitions)
    
    # Now generate the actual features that reference the lookups
    for set_number in sorted(stylistic_sets.keys()):
        substitutions = stylistic_sets[set_number]
        
        if not substitutions:
            continue
        
        # Count special characters in this set
        special_chars_in_set = [s for s in substitutions if is_special_character(s[0])]
        
        feature_lines.append(f"feature ss{set_number:02d} {{")
        feature_lines.append(f"    # Stylistic Set {set_number:02d}")
        
        if special_chars_in_set:
            special_names = [s[0] for s in special_chars_in_set]
            feature_lines.append(f"    # Includes special characters: {', '.join(special_names)}")
        
        feature_lines.append(f"    lookup ss{set_number:02d}_lookup;")
        feature_lines.append(f"}} ss{set_number:02d};")
        feature_lines.append("")
    
    # Add a lookup order comment for InDesign compatibility
    feature_lines.append("# Note: This feature code is optimized for proper glyph order in InDesign:")
    feature_lines.append("# 1. Uses separate lookup definitions for better control")
    feature_lines.append("# 2. Sorts substitutions alphabetically by base glyph name")
    feature_lines.append("# 3. Ensures stylistic set numbers appear in order (.ss01, .ss02, etc.)")
    feature_lines.append("# 4. Base glyphs appear first, then alternates in numerical order")
    feature_lines.append("# 5. Special characters are properly integrated into the sort order")
    feature_lines.append("")
    
    generated_code = "\n".join(feature_lines)
    logging.info(f"Generated features code: {len(feature_lines)} lines for {len(stylistic_sets)} sets")
    
    return generated_code


def ensure_proper_glyph_order(font: RFont, stylistic_sets: Dict[int, List[Tuple[str, str]]]) -> bool:
    """
    Ensure proper glyph ordering for InDesign compatibility.
    This involves checking glyph lib entries and Unicode values for proper sorting.
    
    Args:
        font: Font to modify
        stylistic_sets: Dictionary of stylistic sets data
        
    Returns:
        True if successful, False if failed
    """
    if font is None or not stylistic_sets:
        return False
    
    try:
        # For each stylistic set, ensure alternates have proper lib entries
        for set_number, substitutions in stylistic_sets.items():
            for base_name, alt_name in substitutions:
                if base_name in font and alt_name in font:
                    base_glyph = font[base_name]
                    alt_glyph = font[alt_name]
                    
                    # Ensure alternate has proper lib entry for stylistic set
                    if not hasattr(alt_glyph, 'lib'):
                        continue
                    
                    # Add stylistic set reference in lib
                    alt_glyph.lib[f'public.stylisticSet.ss{set_number:02d}'] = True
                    
                    # Ensure proper glyph order hint for InDesign
                    alt_glyph.lib['public.stylisticSetOrder'] = set_number
                    
                    logging.debug(f"Set lib entries for {alt_name} in ss{set_number:02d}")
        
        logging.info("Applied proper glyph ordering for InDesign compatibility")
        return True
        
    except Exception as error:
        logging.error(f"Failed to set proper glyph order: {error}")
        return False


def apply_features_to_font(font: RFont, features_code: str) -> bool:
    """
    Apply generated features code to the font.
    
    Args:
        font: Font to modify
        features_code: OpenType features code to apply
        
    Returns:
        True if successful, False if failed
    """
    if font is None:
        logging.error("Font is None, cannot apply features")
        return False
    
    if not features_code.strip():
        logging.warning("Features code is empty, nothing to apply")
        return False
    
    try:
        # Get existing features
        existing_features = getattr(font, 'features', None)
        if existing_features is None:
            logging.error("Font does not support features")
            return False
        
        # Get current features text
        current_features = existing_features.text or ""
        
        # Check if auto-generated features already exist and remove them
        lines = current_features.split('\n')
        filtered_lines = []
        skip_auto_generated = False
        
        for line in lines:
            if line.strip().startswith("# Auto-generated stylistic sets"):
                skip_auto_generated = True
                continue
            elif skip_auto_generated and line.strip().startswith("feature ss"):
                # Skip auto-generated feature blocks
                continue
            elif skip_auto_generated and line.strip() == "":
                # Skip empty lines in auto-generated section
                continue
            elif skip_auto_generated and not line.strip().startswith("    ") and not line.strip().startswith("}"):
                # End of auto-generated section
                skip_auto_generated = False
                filtered_lines.append(line)
            elif not skip_auto_generated:
                filtered_lines.append(line)
        
        # Combine existing features with new ones
        if filtered_lines and any(line.strip() for line in filtered_lines):
            combined_features = '\n'.join(filtered_lines).rstrip() + '\n\n' + features_code
        else:
            combined_features = features_code
        
        # Apply to font
        existing_features.text = combined_features
        
        logging.info("Successfully applied features code to font")
        return True
        
    except Exception as error:
        logging.error(f"Failed to apply features to font: {error}")
        return False


def get_processing_summary(stylistic_sets: Dict[int, List[Tuple[str, str]]]) -> Tuple[int, int, int]:
    """
    Get summary of processing results.
    
    Args:
        stylistic_sets: Dictionary of found stylistic sets
        
    Returns:
        Tuple of (total_sets, total_substitutions, special_characters_count)
    """
    total_sets = len(stylistic_sets)
    total_substitutions = sum(len(substitutions) for substitutions in stylistic_sets.values())
    
    # Count special characters across all sets
    special_characters_count = 0
    for substitutions in stylistic_sets.values():
        for base_name, _ in substitutions:
            if is_special_character(base_name):
                special_characters_count += 1
    
    return total_sets, total_substitutions, special_characters_count


def main() -> None:
    """
    Main execution function for MRL Stylistic Sets Auto-Generator.
    """
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Validate current font
        font = validate_current_font()
        if font is None:
            Message("No font is currently open. Please open a font and try again.")
            return
        
        # Scan for stylistic sets
        logging.info("Scanning font for stylistic set alternates...")
        stylistic_sets = scan_font_for_stylistic_sets(font)
        
        if not stylistic_sets:
            Message("No stylistic set alternates found. Make sure your alternate glyphs are named with .ss01, .ss02, etc. suffixes.")
            return
        
        # Generate features code
        logging.info("Generating OpenType features code...")
        features_code = generate_feature_code(stylistic_sets)
        
        if not features_code.strip():
            Message("Failed to generate features code.")
            return
        
        # Ensure proper glyph ordering for InDesign
        logging.info("Setting proper glyph order for InDesign compatibility...")
        ensure_proper_glyph_order(font, stylistic_sets)
        
        # Apply to font
        logging.info("Applying features to font...")
        is_successful = apply_features_to_font(font, features_code)
        
        # Get summary
        total_sets, total_substitutions, special_characters_count = get_processing_summary(stylistic_sets)
        
        # Show completion message
        if is_successful:
            if special_characters_count > 0:
                Message(f"MRL Stylistic Sets Generator completed successfully! Generated {total_sets} stylistic sets with {total_substitutions} substitutions (including {special_characters_count} special characters like underscore, ampersand, etc.). Ready for export!")
            else:
                Message(f"MRL Stylistic Sets Generator completed successfully! Generated {total_sets} stylistic sets with {total_substitutions} substitutions. Ready for export!")
            logging.info("MRL Stylistic Sets Generator completed successfully")
        else:
            Message("MRL Stylistic Sets Generator completed with errors. Check the output window for details.")
            logging.warning("MRL Stylistic Sets Generator completed with errors")
            
    except Exception as error:
        error_message = f"Unexpected error in MRL Stylistic Sets Generator: {error}"
        logging.error(error_message)
        Message(f"An error occurred: {error}")


if __name__ == "__main__":
    main() 