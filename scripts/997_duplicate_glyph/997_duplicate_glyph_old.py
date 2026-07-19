# 997 Duplicate Glyph
# Creates a stylistic alternate from the selected glyph with Command+D
# Version 1.0.0

from mojo.roboFont import CurrentFont, CurrentGlyph
from mojo.UI import OutputWindow
from mojo.events import addObserver, removeObserver
from typing import Dict, List, Optional, Tuple, Any
import objc

# Global observer to prevent garbage collection
_shortcut_observer = None

def get_next_available_ss_number(font: object, base_name: str) -> int:
    """Find the next available stylistic set number."""
    if not font:
        return 1
        
    counter = 1
    while f"{base_name}.ss{counter:02d}" in font:
        counter += 1
    return counter

def has_valid_font_context() -> Tuple[bool, str]:
    """Check if a font is currently open."""
    font = CurrentFont()
    if not font:
        return False, "No font is open"
    return True, ""

def has_valid_glyph_context() -> Tuple[bool, str]:
    """Check if a glyph is currently selected."""
    glyph = CurrentGlyph()
    if not glyph:
        return False, "No glyph is selected"
    return True, ""

def create_stylistic_alternate(font: object, glyph: object) -> Optional[str]:
    """Create a stylistic alternate from the source glyph."""
    try:
        # Determine name for new glyph
        ss_number = get_next_available_ss_number(font, glyph.name)
        new_name = f"{glyph.name}.ss{ss_number:02d}"
        print(f"- Creating new glyph: {new_name}")
        
        # Create new glyph
        new_glyph = font.newGlyph(new_name, clear=True)
        
        # Copy width
        new_glyph.width = glyph.width
        print(f"- Copied width: {glyph.width}")
        
        # Copy contours
        new_glyph.appendGlyph(glyph)
        print(f"- Copied outline data")
        
        # Apply grey color
        new_glyph.markColor = (0.5, 0.5, 0.5, 0.5)
        print(f"- Applied grey color")
        
        # Copy components if any
        for component in glyph.components:
            new_component = component.copy()
            new_glyph.appendComponent(new_component)
        
        # Copy anchors if any
        for anchor in glyph.anchors:
            new_glyph.appendAnchor(anchor.name, (anchor.x, anchor.y))
            
        return new_name
    except Exception as e:
        print(f"Error creating alternate: {str(e)}")
        return None

def position_glyph_after_original(font: object, original_name: str, new_name: str) -> bool:
    """Place the new glyph immediately after the original in glyph order."""
    try:
        if original_name not in font.glyphOrder:
            print(f"- Warning: Original glyph {original_name} not in glyph order")
            return False
            
        # Get current glyph order
        order_index = font.glyphOrder.index(original_name)
        new_order = list(font.glyphOrder)
        print(f"- Found original at position {order_index}")
        
        # Remove new glyph if it exists elsewhere in the order
        if new_name in new_order:
            new_order.remove(new_name)
            print(f"- Removed existing {new_name} from glyph order")
            
        # Insert new glyph right after the original
        new_order.insert(order_index + 1, new_name)
        font.glyphOrder = new_order
        print(f"- Positioned {new_name} after {original_name}")
        return True
    except Exception as e:
        print(f"Error positioning glyph in order: {str(e)}")
        return False

def duplicate_as_stylistic_alternate() -> bool:
    """Main function to duplicate the current glyph as a stylistic alternate."""
    print("Starting duplication process...")
    
    # Early returns for invalid contexts
    is_font_valid, font_error = has_valid_font_context()
    if not is_font_valid:
        print(f"Error: {font_error}")
        return False
        
    is_glyph_valid, glyph_error = has_valid_glyph_context()
    if not is_glyph_valid:
        print(f"Error: {glyph_error}")
        return False
    
    # Get current contexts
    font = CurrentFont()
    glyph = CurrentGlyph()
    
    print(f"Font: {font.info.familyName}")
    print(f"Selected glyph: {glyph.name}")
    
    # Create the alternate
    print(f"Duplicating '{glyph.name}'...")
    new_name = create_stylistic_alternate(font, glyph)
    if not new_name:
        return False
    
    # Position after original
    if not position_glyph_after_original(font, glyph.name, new_name):
        print(f"Warning: Could not position {new_name} after {glyph.name}")
    
    # Update font
    font.changed()
    print(f"Success: Created {new_name} after {glyph.name}")
    return True

# For direct manual execution
def run_duplicate_now() -> None:
    """Run the duplication immediately without waiting for a shortcut."""
    output = OutputWindow()
    output.clear()
    output.show()
    duplicate_as_stylistic_alternate()

def key_down_callback(sender: Any, info: Dict) -> None:
    """Process keyboard events."""
    try:
        # Check if it's Command+D
        key_char = info.get('characters', '')
        if not key_char:
            return
            
        is_d_key = key_char.lower() == 'd'
        is_command_down = info.get('commandDown', False)
        
        if is_d_key and is_command_down:
            print("Command+D detected!")
            duplicate_as_stylistic_alternate()
    except Exception as e:
        print(f"Error in key handler: {str(e)}")

def setup_command_d_shortcut() -> None:
    """Set up the Command+D keyboard shortcut."""
    global _shortcut_observer
    
    # Show output window
    output = OutputWindow()
    output.clear()
    output.show()
    
    # Clear any existing observers
    if _shortcut_observer:
        try:
            removeObserver(_shortcut_observer, "keyDown")
        except:
            pass
    
    # Create a new NSObject-based observer that won't get garbage collected
    _shortcut_observer = objc.lookUpClass("NSObject").alloc().init()
    
    # Add our callback method to the observer
    _shortcut_observer.keyDown = key_down_callback
    
    # Register observer
    addObserver(_shortcut_observer, "keyDown", "keyDown")
    print("✓ Command+D shortcut installed")
    print("✓ Select a glyph and press Command+D to duplicate it as a stylistic alternate")

# Run when script is executed
if __name__ == '__main__':
    # First try direct duplication
    run_duplicate_now()
    
    # Then set up the keyboard shortcut
    setup_command_d_shortcut() 