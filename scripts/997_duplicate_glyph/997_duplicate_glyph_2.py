# 997 Duplicate Glyph - Fixed Version
# Creates stylistic alternates from selected glyphs with Command+D
# Version 2.0.0 - Now supports multiple selected glyphs

from mojo.roboFont import CurrentFont
from mojo.UI import OutputWindow
from mojo.events import addObserver, removeObserver
from mojo.subscriber import Subscriber
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom Error Types
class FontError(Exception):
    """Custom error for font-related issues."""
    pass

class GlyphError(Exception):
    """Custom error for glyph-related issues."""
    pass

class ProcessingError(Exception):
    """Custom error for processing failures."""
    pass

# Global subscriber instance
_keyboard_subscriber: Optional['KeyboardSubscriber'] = None

def get_next_available_ss_number(font: object, base_name: str) -> int:
    """Find the next available stylistic set number for a glyph.
    
    Args:
        font: The current font object
        base_name: Base name of the glyph
        
    Returns:
        Next available SS number
        
    Raises:
        FontError: If font is invalid
    """
    if not font:
        raise FontError("Font object is None")
        
    counter = 1
    while f"{base_name}.ss{counter:02d}" in font:
        counter += 1
    return counter

def validate_font_context() -> object:
    """Validate and return current font context.
    
    Returns:
        Current font object
        
    Raises:
        FontError: If no font is open
    """
    font = CurrentFont()
    if not font:
        raise FontError("No font is open")
    return font

def get_selected_glyphs() -> List[object]:
    """Get all currently selected glyphs.
    
    Returns:
        List of selected glyph objects
        
    Raises:
        FontError: If no font is open
        GlyphError: If no glyphs are selected
    """
    font = validate_font_context()
    selected_glyphs = list(font.selectedGlyphs)
    
    if not selected_glyphs:
        raise GlyphError("No glyphs are selected")
    
    return selected_glyphs

def create_stylistic_alternate(font: object, source_glyph: object) -> Optional[str]:
    """Create a stylistic alternate from a source glyph.
    
    Args:
        font: The font object
        source_glyph: The source glyph to duplicate
        
    Returns:
        Name of created alternate or None if failed
        
    Raises:
        ProcessingError: If creation fails
    """
    try:
        # Determine name for new glyph
        ss_number = get_next_available_ss_number(font, source_glyph.name)
        new_name = f"{source_glyph.name}.ss{ss_number:02d}"
        logger.info(f"Creating new glyph: {new_name}")
        
        # Create new glyph
        new_glyph = font.newGlyph(new_name, clear=True)
        
        # Copy metrics
        new_glyph.width = source_glyph.width
        logger.info(f"Copied width: {source_glyph.width}")
        
        # Copy outline data
        new_glyph.appendGlyph(source_glyph)
        logger.info("Copied outline data")
        
        # Apply grey color
        new_glyph.markColor = (0.5, 0.5, 0.5, 0.5)
        logger.info("Applied grey color")
        
        # Copy components if any
        for component in source_glyph.components:
            new_component = component.copy()
            new_glyph.appendComponent(new_component)
        
        # Copy anchors if any
        for anchor in source_glyph.anchors:
            new_glyph.appendAnchor(anchor.name, (anchor.x, anchor.y))
            
        return new_name
        
    except Exception as e:
        raise ProcessingError(f"Failed to create alternate for {source_glyph.name}: {str(e)}")

def position_glyph_after_original(font: object, original_name: str, new_name: str) -> bool:
    """Position new glyph immediately after original in glyph order.
    
    Args:
        font: The font object
        original_name: Name of original glyph
        new_name: Name of new glyph
        
    Returns:
        True if positioning succeeded
        
    Raises:
        ProcessingError: If positioning fails
    """
    try:
        if original_name not in font.glyphOrder:
            logger.warning(f"Original glyph {original_name} not in glyph order")
            return False
            
        # Get current glyph order
        order_index = font.glyphOrder.index(original_name)
        new_order = list(font.glyphOrder)
        logger.info(f"Found original at position {order_index}")
        
        # Remove new glyph if it exists elsewhere in the order
        if new_name in new_order:
            new_order.remove(new_name)
            logger.info(f"Removed existing {new_name} from glyph order")
            
        # Insert new glyph right after the original
        new_order.insert(order_index + 1, new_name)
        font.glyphOrder = new_order
        logger.info(f"Positioned {new_name} after {original_name}")
        return True
        
    except Exception as e:
        raise ProcessingError(f"Failed to position glyph: {str(e)}")

def process_glyph_duplication(source_glyph: object, font: object) -> str:
    """Process duplication of a single glyph.
    
    Args:
        source_glyph: Glyph to duplicate
        font: Font object
        
    Returns:
        Name of created alternate
        
    Raises:
        ProcessingError: If duplication fails
    """
    logger.info(f"Processing glyph: {source_glyph.name}")
    
    # Create the alternate
    new_name = create_stylistic_alternate(font, source_glyph)
    if not new_name:
        raise ProcessingError(f"Failed to create alternate for {source_glyph.name}")
    
    # Position after original
    success = position_glyph_after_original(font, source_glyph.name, new_name)
    if not success:
        logger.warning(f"Could not position {new_name} after {source_glyph.name}")
    
    return new_name

def duplicate_selected_glyphs() -> bool:
    """Main function to duplicate all selected glyphs as stylistic alternates.
    
    Returns:
        True if all duplications succeeded
        
    Raises:
        FontError: If font context is invalid
        GlyphError: If no glyphs are selected
        ProcessingError: If duplication fails
    """
    logger.info("Starting batch duplication process...")
    
    try:
        # Validate contexts
        font = validate_font_context()
        selected_glyphs = get_selected_glyphs()
        
        logger.info(f"Font: {font.info.familyName}")
        logger.info(f"Selected glyphs: {len(selected_glyphs)}")
        
        # Process each selected glyph
        created_alternates = []
        failed_glyphs = []
        
        for glyph in selected_glyphs:
            try:
                new_name = process_glyph_duplication(glyph, font)
                created_alternates.append(new_name)
                logger.info(f"✓ Successfully created {new_name}")
                
            except ProcessingError as e:
                logger.error(f"✗ Failed to process {glyph.name}: {str(e)}")
                failed_glyphs.append(glyph.name)
                continue
        
        # Update font
        font.changed()
        
        # Log results
        logger.info(f"Batch duplication completed:")
        logger.info(f"  ✓ Created: {len(created_alternates)} alternates")
        logger.info(f"  ✗ Failed: {len(failed_glyphs)} glyphs")
        
        if created_alternates:
            logger.info(f"  Created alternates: {', '.join(created_alternates)}")
        
        if failed_glyphs:
            logger.warning(f"  Failed glyphs: {', '.join(failed_glyphs)}")
        
        return len(failed_glyphs) == 0
        
    except (FontError, GlyphError) as e:
        logger.error(f"Context error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def run_duplicate_now() -> None:
    """Run duplication immediately without waiting for shortcut."""
    output = OutputWindow()
    output.clear()
    output.show()
    
    try:
        success = duplicate_selected_glyphs()
        if success:
            logger.info("All glyphs duplicated successfully!")
        else:
            logger.warning("Some glyphs failed to duplicate. Check log for details.")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")

class KeyboardSubscriber(Subscriber):
    """Subscriber for handling keyboard events using proper Subscriber pattern."""
    
    def build(self):
        """Initialize the subscriber."""
        logger.info("Keyboard subscriber initialized")
    
    def keyDown(self, info: Dict[str, Any]) -> None:
        """Process keyboard events.
        
        Args:
            info: Event info dictionary
        """
        try:
            # Check if it's Command+D
            key_char = info.get('characters', '')
            if not key_char:
                return
                
            is_d_key = key_char.lower() == 'd'
            is_command_down = info.get('commandDown', False)
            
            if is_d_key and is_command_down:
                logger.info("Command+D detected!")
                duplicate_selected_glyphs()
                
        except Exception as e:
            logger.error(f"Error in key handler: {str(e)}")

def setup_command_d_shortcut() -> None:
    """Set up the Command+D keyboard shortcut using proper Subscriber pattern."""
    global _keyboard_subscriber
    
    # Show output window
    output = OutputWindow()
    output.clear()
    output.show()
    
    # Clean up existing subscriber
    if _keyboard_subscriber:
        _keyboard_subscriber.destroy()
    
    # Create new subscriber
    _keyboard_subscriber = KeyboardSubscriber()
    _keyboard_subscriber.controller = _keyboard_subscriber  # Required for proper subscriber pattern
    
    logger.info("✓ Command+D shortcut installed using Subscriber pattern")
    logger.info("✓ Select one or more glyphs and press Command+D to duplicate them as stylistic alternates")

def cleanup_subscriber() -> None:
    """Clean up the keyboard subscriber."""
    global _keyboard_subscriber
    if _keyboard_subscriber:
        _keyboard_subscriber.destroy()
        _keyboard_subscriber = None
        logger.info("Keyboard subscriber cleaned up")

# Run when script is executed
if __name__ == '__main__':
    try:
        # First try direct duplication of selected glyphs
        run_duplicate_now()
        
        # Then set up the keyboard shortcut
        setup_command_d_shortcut()
        
    except Exception as e:
        logger.error(f"Script initialization failed: {str(e)}")
        print(f"Error: {str(e)}") 