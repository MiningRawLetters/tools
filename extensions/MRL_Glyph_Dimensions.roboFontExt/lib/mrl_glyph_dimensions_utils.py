# MRL Glyph Dimensions Utilities
# Developed by Kevin Kuhn (Mining Raw Letters)

"""
Utility functions for MRL Glyph Dimensions extension.
Provides common operations for glyph dimension management.
"""

from typing import Optional, List, Tuple, Dict, Any
import logging

# RoboFont and FontParts imports
try:
    from mojo.roboFont import CurrentFont, AllFonts
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
    
    # Skip special glyphs (starting with dot)
    if glyph_name.startswith('.'):
        logging.info(f"Glyph '{glyph_name}' is a special glyph, skipping")
        return False
        
    return True


def apply_glyph_horizontal_metrics(glyph, glyph_name: str, target_width: int, left_margin: int) -> bool:
    """
    Apply specified horizontal metrics to a single glyph, preserving outline width.
    
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
        
        # Ensure right margin doesn't go below 0
        new_right_margin = max(0, new_right_margin)
        
        # Apply new metrics
        glyph.width = target_width
        glyph.leftMargin = left_margin
        glyph.rightMargin = new_right_margin
        
        logging.info(f"Updated '{glyph_name}': W{original_width}→{target_width}, L{original_left}→{left_margin}, R{original_right}→{new_right_margin} (outline:{outline_width})")
        return True
        
    except Exception as glyph_error:
        logging.error(f"Failed to update glyph '{glyph_name}': {glyph_error}")
        return False


def apply_batch_horizontal_metrics(font: RFont, target_width: int, left_margin: int) -> Tuple[int, int]:
    """
    Apply uniform horizontal metrics to all glyphs in a font, preserving outline widths.
    
    Args:
        font: The font to modify
        target_width: Total advance width in units
        left_margin: Left side bearing value in units
        
    Returns:
        Tuple of (successful_updates, failed_updates)
    """
    if font is None:
        logging.error("Font is None, cannot process")
        return 0, 0
    
    successful_updates = 0
    failed_updates = 0
    
    # Process each glyph
    for glyph_name in font.keys():
        glyph = font[glyph_name]
        
        if apply_glyph_horizontal_metrics(glyph, glyph_name, target_width, left_margin):
            successful_updates += 1
        else:
            failed_updates += 1
    
    # Mark font as changed
    font.changed()
    
    logging.info(f"Batch horizontal metrics complete: {successful_updates} successful, {failed_updates} failed")
    return successful_updates, failed_updates


def apply_vertical_metrics(font: RFont, metrics: Dict[str, int]) -> bool:
    """
    Apply vertical metrics to a font.
    
    Args:
        font: The font to modify
        metrics: Dictionary containing metric values:
            - units_per_em: Units per em
            - ascender: Ascender value
            - descender: Descender value
            - cap_height: Cap height value
            - x_height: X-height value
            
    Returns:
        True if successful, False if failed
    """
    if font is None:
        logging.error("Font is None, cannot apply vertical metrics")
        return False
    
    try:
        # Apply basic font info values
        if 'units_per_em' in metrics:
            font.info.unitsPerEm = metrics['units_per_em']
        if 'ascender' in metrics:
            font.info.ascender = metrics['ascender']
        if 'descender' in metrics:
            font.info.descender = metrics['descender']
        if 'cap_height' in metrics:
            font.info.capHeight = metrics['cap_height']
        if 'x_height' in metrics:
            font.info.xHeight = metrics['x_height']
        
        # Mark font as changed
        font.changed()
        
        logging.info(f"Applied vertical metrics to font: {metrics}")
        return True
        
    except Exception as error:
        logging.error(f"Failed to apply vertical metrics: {error}")
        return False


def apply_webfont_strategy(font: RFont, metrics: Dict[str, int]) -> bool:
    """
    Apply webfont strategy for cross-platform consistency.
    
    Args:
        font: The font to modify
        metrics: Dictionary containing metric values (same as apply_vertical_metrics)
            
    Returns:
        True if successful, False if failed
    """
    if font is None:
        logging.error("Font is None, cannot apply webfont strategy")
        return False
    
    try:
        # Apply basic vertical metrics first
        if not apply_vertical_metrics(font, metrics):
            return False
        
        # Get values for OpenType metrics
        ascender = metrics.get('ascender', font.info.ascender)
        descender = metrics.get('descender', font.info.descender)
        
        # sTypo metrics (for modern apps)
        font.info.openTypeOS2TypoAscender = ascender
        font.info.openTypeOS2TypoDescender = descender
        font.info.openTypeOS2TypoLineGap = 0
        
        # hhea metrics (for macOS/Linux)
        font.info.openTypeHheaAscender = ascender
        font.info.openTypeHheaDescender = descender
        font.info.openTypeHheaLineGap = 0
        
        # win metrics (for Windows)
        font.info.openTypeOS2WinAscent = ascender
        font.info.openTypeOS2WinDescent = abs(descender)
        
        # Set the 'useTypoMetrics' flag (fsSelection bit 7)
        if font.info.openTypeOS2Selection:
            if 7 not in font.info.openTypeOS2Selection:
                font.info.openTypeOS2Selection.append(7)
        else:
            font.info.openTypeOS2Selection = [7]
        
        # Mark font as changed
        font.changed()
        
        logging.info(f"Applied webfont strategy to font with metrics: {metrics}")
        return True
        
    except Exception as error:
        logging.error(f"Failed to apply webfont strategy: {error}")
        return False


def get_font_metrics_summary(font: RFont) -> Dict[str, Any]:
    """
    Get a summary of current font metrics.
    
    Args:
        font: The font to analyze
        
    Returns:
        Dictionary containing font metrics summary
    """
    if font is None:
        return {}
    
    try:
        summary = {
            'font_name': f"{font.info.familyName} {font.info.styleName}",
            'glyph_count': len(font),
            'units_per_em': font.info.unitsPerEm,
            'ascender': font.info.ascender,
            'descender': font.info.descender,
            'cap_height': font.info.capHeight,
            'x_height': font.info.xHeight,
            'horizontal_metrics': {
                'total_glyphs': len(font),
                'glyphs_with_width': 0,
                'average_width': 0,
                'min_width': float('inf'),
                'max_width': 0
            }
        }
        
        # Calculate horizontal metrics statistics
        total_width = 0
        glyphs_with_width = 0
        
        for glyph_name in font.keys():
            glyph = font[glyph_name]
            if hasattr(glyph, 'width') and glyph.width is not None:
                width = glyph.width
                total_width += width
                glyphs_with_width += 1
                summary['horizontal_metrics']['min_width'] = min(summary['horizontal_metrics']['min_width'], width)
                summary['horizontal_metrics']['max_width'] = max(summary['horizontal_metrics']['max_width'], width)
        
        if glyphs_with_width > 0:
            summary['horizontal_metrics']['glyphs_with_width'] = glyphs_with_width
            summary['horizontal_metrics']['average_width'] = total_width / glyphs_with_width
        else:
            summary['horizontal_metrics']['min_width'] = 0
        
        return summary
        
    except Exception as error:
        logging.error(f"Failed to get font metrics summary: {error}")
        return {}


def get_glyph_metrics(glyph) -> Dict[str, Any]:
    """
    Get metrics for a specific glyph.
    
    Args:
        glyph: The glyph object
        
    Returns:
        Dictionary containing glyph metrics
    """
    if glyph is None:
        return {}
    
    try:
        metrics = {
            'name': glyph.name,
            'width': getattr(glyph, 'width', 0),
            'left_margin': getattr(glyph, 'leftMargin', 0),
            'right_margin': getattr(glyph, 'rightMargin', 0),
            'bounds': glyph.bounds if hasattr(glyph, 'bounds') else None
        }
        
        # Calculate outline width
        metrics['outline_width'] = metrics['width'] - metrics['left_margin'] - metrics['right_margin']
        
        return metrics
        
    except Exception as error:
        logging.error(f"Failed to get glyph metrics: {error}")
        return {}


def validate_metric_value(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> Optional[int]:
    """
    Validate a metric value.
    
    Args:
        value: The value to validate
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
        
    Returns:
        Validated integer value or None if invalid
    """
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            logging.warning(f"Value {int_value} is below minimum {min_value}")
            return None
            
        if max_value is not None and int_value > max_value:
            logging.warning(f"Value {int_value} is above maximum {max_value}")
            return None
            
        return int_value
        
    except (ValueError, TypeError):
        logging.warning(f"Invalid value: {value}")
        return None


# Preset configurations
PRESET_CONFIGURATIONS = {
    '900_width': {
        'name': '900 Width',
        'description': 'Standard 900-unit width with 90-unit sidebearings',
        'horizontal': {
            'target_width': 900,
            'left_margin': 90
        }
    },
    '1000_width': {
        'name': '1000 Width',
        'description': 'Standard 1000-unit width with 100-unit sidebearings',
        'horizontal': {
            'target_width': 1000,
            'left_margin': 100
        }
    },
    'webfont': {
        'name': 'Webfont',
        'description': 'Cross-platform consistent webfont metrics',
        'vertical': {
            'units_per_em': 1000,
            'ascender': 810,
            'descender': -90,
            'cap_height': 720,
            'x_height': 500
        }
    }
}


def get_preset_configuration(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a preset configuration by name.
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        Preset configuration dictionary or None if not found
    """
    return PRESET_CONFIGURATIONS.get(preset_name)


def list_preset_configurations() -> List[str]:
    """
    Get list of available preset configuration names.
    
    Returns:
        List of preset names
    """
    return list(PRESET_CONFIGURATIONS.keys()) 