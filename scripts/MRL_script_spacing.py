#!/usr/bin/env python3
"""
MRL Script Spacing

A RoboFont script that sets glyph metrics to:
- Total width: 900 units
- Left side bearing: 90 units  
- Right side bearing: 90 units

Follows functional/declarative programming paradigm with proper error handling.

Author: Master 977 & Codette
"""

from typing import Optional, List, Tuple
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


def validate_current_font() -> Optional[RFont]:
    """
    Validate that a font is currently open in RoboFont.
    
    Returns:
        Font object if valid, None if no font is open
        
    Raises:
        RuntimeError: If no font is currently open
    """
    current_font = CurrentFont()
    
    if current_font is None:
        raise RuntimeError("No font is currently open in RoboFont")
    
    return current_font


def should_process_glyph(glyph_name: str, glyph) -> bool:
    """
    Determine if a glyph should have its metrics modified.
    
    Args:
        glyph_name: Name of the glyph
        glyph: The glyph object
        
    Returns:
        True if glyph should be processed, False otherwise
    """
    if glyph is None:
        logging.warning(f"Glyph '{glyph_name}' is None, skipping")
        return False
    
    # Skip empty glyphs that might not need spacing
    if not hasattr(glyph, 'width'):
        logging.warning(f"Glyph '{glyph_name}' has no width attribute, skipping")
        return False
        
    return True


def apply_glyph_metrics(glyph, glyph_name: str, target_width: int, left_margin: int) -> bool:
    """
    Apply specified metrics to a single glyph, preserving outline width.
    
    Args:
        glyph: The glyph object to modify
        glyph_name: Name of the glyph for logging
        target_width: Total advance width in units
        left_margin: Left side bearing value in units
        
    Returns:
        True if successful, False if failed
    """
    if not should_process_glyph(glyph_name, glyph):
        return False
    
    try:
        # Store original values for logging
        original_width = getattr(glyph, 'width', 0)
        original_left = getattr(glyph, 'leftMargin', 0)
        original_right = getattr(glyph, 'rightMargin', 0)
        
        # Calculate current outline width
        outline_width = original_width - original_left - original_right
        
        # Calculate new right margin to preserve outline width
        new_right_margin = target_width - left_margin - outline_width
        
        # Apply new metrics
        glyph.width = target_width
        glyph.leftMargin = left_margin
        glyph.rightMargin = new_right_margin
        
        logging.info(f"Updated '{glyph_name}': W{original_width}→{target_width}, L{original_left}→{left_margin}, R{original_right}→{new_right_margin} (outline:{outline_width})")
        return True
        
    except Exception as glyph_error:
        logging.error(f"Failed to update glyph '{glyph_name}': {glyph_error}")
        return False


def get_glyph_processing_summary(font: RFont) -> Tuple[int, List[str]]:
    """
    Analyze font and return processing summary.
    
    Args:
        font: The font to analyze
        
    Returns:
        Tuple of (total_glyphs_count, list_of_glyph_names)
    """
    glyph_names = list(font.keys())
    total_count = len(glyph_names)
    
    logging.info(f"Font contains {total_count} glyphs")
    return total_count, glyph_names


def apply_uniform_metrics_to_font(font: RFont, target_width: int = 900, left_margin: int = 90) -> bool:
    """
    Apply uniform metrics to all glyphs in a font, preserving outline widths.
    
    Args:
        font: The font to modify
        target_width: Total advance width in units (default: 900)
        left_margin: Left side bearing value in units (default: 90)
        
    Returns:
        True if all glyphs processed successfully, False if errors occurred
    """
    if font is None:
        logging.error("Font is None, cannot process")
        return False
    
    total_glyphs, glyph_names = get_glyph_processing_summary(font)
    
    if total_glyphs == 0:
        logging.warning("Font contains no glyphs")
        return True
    
    successful_updates = 0
    failed_updates = 0
    
    # Process each glyph
    for glyph_name in glyph_names:
        glyph = font[glyph_name]
        
        if apply_glyph_metrics(glyph, glyph_name, target_width, left_margin):
            successful_updates += 1
        else:
            failed_updates += 1
    
    # Log summary
    logging.info(f"Processing complete: {successful_updates} successful, {failed_updates} failed")
    
    return failed_updates == 0


def execute_mrl_script_spacing() -> None:
    """
    Main execution function for MRL Script Spacing.
    Applies uniform metrics (width=900, left=90, right=90) to all glyphs in the current font.
    """
    try:
        # Validate current font
        current_font = validate_current_font()
        
        # Log start of operation
        font_name = getattr(current_font.info, 'familyName', 'Unnamed Font')
        logging.info(f"Starting MRL Script Spacing on font: {font_name}")
        
        # Apply uniform metrics
        is_successful = apply_uniform_metrics_to_font(current_font)
        
        # Show completion message
        if is_successful:
            Message("MRL Script Spacing completed successfully! All glyphs now have width=900, left=90, with preserved outline widths.")
            logging.info("MRL Script Spacing completed successfully")
        else:
            Message("MRL Script Spacing completed with some errors. Check the output window for details.")
            logging.warning("MRL Script Spacing completed with errors")
            
    except RuntimeError as runtime_error:
        error_message = f"Runtime error: {runtime_error}"
        Message(error_message)
        logging.error(error_message)
        
    except Exception as unexpected_error:
        error_message = f"Unexpected error in MRL Script Spacing: {unexpected_error}"
        Message(error_message)
        logging.error(error_message)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Execute the script when run directly
if __name__ == "__main__":
    execute_mrl_script_spacing() 