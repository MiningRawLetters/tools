# 997 Duplicate Glyph v3.0
# Professional-grade script for creating stylistic alternates from selected glyphs
# Supports multiple selection, batch processing, and advanced configuration
# Version 3.0.0 by Codette for Master 977

from mojo.roboFont import CurrentFont
from mojo.UI import OutputWindow
from mojo.subscriber import Subscriber, registerGlyphEditorSubscriber, unregisterGlyphEditorSubscriber
from mojo.events import addObserver, removeObserver
from typing import Dict, List, Optional, Tuple, Set, Union, Any, NamedTuple
from dataclasses import dataclass
from contextlib import contextmanager
import logging
import time
import weakref

# Configure professional logging with debug enabled
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DuplicateGlyph')

# Type aliases for clarity
FontObject = Any  # RFont object
GlyphObject = Any  # RGlyph object

# Custom Error Hierarchy
class DuplicateGlyphError(Exception):
    """Base exception for all duplicate glyph operations."""
    pass

class FontContextError(DuplicateGlyphError):
    """Font-related validation errors."""
    pass

class GlyphSelectionError(DuplicateGlyphError):
    """Glyph selection validation errors."""
    pass

class ProcessingError(DuplicateGlyphError):
    """Processing operation failures."""
    pass

class ConfigurationError(DuplicateGlyphError):
    """Configuration validation errors."""
    pass

# Configuration and Result Types
@dataclass
class ProcessingConfig:
    """Configuration for glyph duplication operations."""
    suffix_pattern: str = "ss"
    start_number: int = 1
    apply_color: bool = True
    color: Tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.5)
    copy_components: bool = True
    copy_anchors: bool = True
    position_after_original: bool = True
    show_progress: bool = True
    validate_compatibility: bool = True

class ProcessingResult(NamedTuple):
    """Result of a single glyph processing operation."""
    success: bool
    glyph_name: str
    alternate_name: Optional[str]
    error_message: Optional[str]
    processing_time: float

@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total_processed: int
    successful: List[ProcessingResult]
    failed: List[ProcessingResult]
    total_time: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_processed == 0:
            return 0.0
        return (len(self.successful) / self.total_processed) * 100

# Global registry for cleanup
_active_subscribers: Set[weakref.ReferenceType] = set()

class DuplicateGlyphProcessor:
    """Professional glyph duplication processor with advanced features."""
    
    def __init__(self, config: ProcessingConfig = None):
        """Initialize processor with configuration.
        
        Args:
            config: Processing configuration, uses defaults if None
        """
        self.config = config or ProcessingConfig()
        self._validate_configuration()
        logger.info(f"Processor initialized with config: {self.config}")
    
    def _validate_configuration(self) -> None:
        """Validate processor configuration.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if self.config.start_number < 1:
            raise ConfigurationError("start_number must be >= 1")
        
        if not self.config.suffix_pattern.strip():
            raise ConfigurationError("suffix_pattern cannot be empty")
        
        if len(self.config.color) != 4:
            raise ConfigurationError("color must be RGBA tuple with 4 values")
        
        if not all(0 <= c <= 1 for c in self.config.color):
            raise ConfigurationError("color values must be between 0 and 1")
    
    def get_current_font(self) -> FontObject:
        """Get and validate current font context.
        
        Returns:
            Current font object
            
        Raises:
            FontContextError: If no font is available
        """
        font = CurrentFont()
        if not font:
            raise FontContextError("No font is currently open")
        
        if not hasattr(font, 'glyphs'):
            raise FontContextError("Font object appears to be corrupted")
        
        return font
    
    def get_selected_glyphs(self) -> List[GlyphObject]:
        """Get all currently selected glyphs with validation.
        
        Returns:
            List of selected glyph objects
            
        Raises:
            FontContextError: If font context is invalid
            GlyphSelectionError: If no glyphs are selected or selection is invalid
        """
        font = self.get_current_font()
        
        if not hasattr(font, 'selectedGlyphs'):
            raise FontContextError("Font does not support glyph selection")
        
        selected_glyphs = list(font.selectedGlyphs)
        
        if not selected_glyphs:
            raise GlyphSelectionError("No glyphs are currently selected")
        
        # Validate glyph objects
        invalid_glyphs = [g for g in selected_glyphs if not hasattr(g, 'name')]
        if invalid_glyphs:
            raise GlyphSelectionError(f"Invalid glyph objects detected: {len(invalid_glyphs)}")
        
        return selected_glyphs
    
    def find_next_available_number(self, font: FontObject, base_name: str) -> int:
        """Find next available number for stylistic alternate.
        
        Args:
            font: Font object to search in
            base_name: Base name of the glyph
            
        Returns:
            Next available number
            
        Raises:
            ProcessingError: If unable to find available number
        """
        counter = self.config.start_number
        max_attempts = 1000  # Prevent infinite loops
        
        while counter < max_attempts:
            alternate_name = f"{base_name}.{self.config.suffix_pattern}{counter:02d}"
            if alternate_name not in font:
                return counter
            counter += 1
        
        raise ProcessingError(f"Unable to find available number for {base_name} after {max_attempts} attempts")
    
    def create_alternate_glyph(self, font: FontObject, source_glyph: GlyphObject) -> str:
        """Create a stylistic alternate from source glyph with full feature set.
        
        Args:
            font: Font object
            source_glyph: Source glyph to duplicate
            
        Returns:
            Name of created alternate
            
        Raises:
            ProcessingError: If creation fails
        """
        try:
            # Find available number
            number = self.find_next_available_number(font, source_glyph.name)
            alternate_name = f"{source_glyph.name}.{self.config.suffix_pattern}{number:02d}"
            
            logger.debug(f"Creating alternate: {alternate_name}")
            
            # Create new glyph with proper cleanup
            if alternate_name in font:
                del font[alternate_name]  # Clean up any existing glyph
            
            alternate_glyph = font.newGlyph(alternate_name, clear=True)
            
            # Copy metrics with validation
            if hasattr(source_glyph, 'width') and source_glyph.width is not None:
                alternate_glyph.width = source_glyph.width
            
            # Copy outline data
            alternate_glyph.appendGlyph(source_glyph)
            
            # Copy components if configured
            if self.config.copy_components and hasattr(source_glyph, 'components'):
                for component in source_glyph.components:
                    try:
                        new_component = component.copy()
                        alternate_glyph.appendComponent(new_component)
                    except Exception as e:
                        logger.warning(f"Failed to copy component in {source_glyph.name}: {e}")
            
            # Copy anchors if configured
            if self.config.copy_anchors and hasattr(source_glyph, 'anchors'):
                for anchor in source_glyph.anchors:
                    try:
                        alternate_glyph.appendAnchor(anchor.name, (anchor.x, anchor.y))
                    except Exception as e:
                        logger.warning(f"Failed to copy anchor {anchor.name} in {source_glyph.name}: {e}")
            
            # Apply color marking if configured
            if self.config.apply_color:
                alternate_glyph.markColor = self.config.color
            
            logger.info(f"✓ Created alternate: {alternate_name}")
            return alternate_name
            
        except Exception as e:
            raise ProcessingError(f"Failed to create alternate for {source_glyph.name}: {str(e)}")
    
    def position_glyph_optimally(self, font: FontObject, original_name: str, alternate_name: str) -> bool:
        """Position alternate glyph optimally in glyph order with enhanced reliability.
        
        Args:
            font: Font object
            original_name: Name of original glyph
            alternate_name: Name of alternate glyph
            
        Returns:
            True if positioning succeeded
        """
        if not self.config.position_after_original:
            return True
        
        try:
            # Ensure font has glyph order attribute
            if not hasattr(font, 'glyphOrder'):
                logger.debug(f"Font has no glyphOrder attribute, creating one")
                font.glyphOrder = list(font.keys())
            
            # Ensure original glyph is in glyph order
            if original_name not in font.glyphOrder:
                logger.debug(f"Adding {original_name} to glyph order")
                font.glyphOrder.append(original_name)
            
            # Get current order as a working copy
            current_order = list(font.glyphOrder)
            logger.debug(f"Current glyph order length: {len(current_order)}")
            
            # Find position of original glyph
            try:
                original_index = current_order.index(original_name)
            except ValueError:
                logger.error(f"Cannot find {original_name} in glyph order")
                return False
            
            # Remove alternate if it exists elsewhere (cleanup)
            while alternate_name in current_order:
                current_order.remove(alternate_name)
                logger.debug(f"Removed existing {alternate_name} from position")
            
            # Recalculate original index after cleanup
            try:
                original_index = current_order.index(original_name)
            except ValueError:
                logger.error(f"Lost {original_name} during cleanup")
                return False
            
            # Insert alternate right after original
            insert_position = original_index + 1
            current_order.insert(insert_position, alternate_name)
            
            # Validate the new order
            if len(current_order) != len(set(current_order)):
                logger.error(f"Duplicate entries detected in new glyph order")
                return False
            
            # Apply the new order
            font.glyphOrder = current_order
            logger.info(f"✓ Positioned {alternate_name} at index {insert_position} (after {original_name})")
            
            # Verify the positioning worked
            verification_index = font.glyphOrder.index(alternate_name)
            if verification_index == insert_position:
                return True
            else:
                logger.warning(f"Position verification failed: expected {insert_position}, got {verification_index}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to position {alternate_name}: {e}")
            import traceback
            logger.debug(f"Positioning error traceback: {traceback.format_exc()}")
            return False
    
    def process_single_glyph(self, font: FontObject, glyph: GlyphObject) -> ProcessingResult:
        """Process a single glyph with comprehensive error handling.
        
        Args:
            font: Font object
            glyph: Glyph to process
            
        Returns:
            ProcessingResult with operation details
        """
        start_time = time.time()
        glyph_name = getattr(glyph, 'name', 'unknown')
        
        try:
            # Validate glyph compatibility if configured
            if self.config.validate_compatibility and hasattr(glyph, 'layers'):
                if not glyph.layers:
                    raise ProcessingError(f"Glyph {glyph_name} has no layers")
            
            # Create alternate
            alternate_name = self.create_alternate_glyph(font, glyph)
            
            # Position optimally
            positioning_success = self.position_glyph_optimally(font, glyph_name, alternate_name)
            if not positioning_success:
                logger.warning(f"Positioning failed for {alternate_name}, but glyph was created")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                glyph_name=glyph_name,
                alternate_name=alternate_name,
                error_message=None,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Failed to process {glyph_name}: {error_msg}")
            
            return ProcessingResult(
                success=False,
                glyph_name=glyph_name,
                alternate_name=None,
                error_message=error_msg,
                processing_time=processing_time
            )
    
    def process_batch(self) -> BatchResult:
        """Process all selected glyphs in batch with comprehensive reporting.
        
        Returns:
            BatchResult with complete operation statistics
            
        Raises:
            FontContextError: If font context is invalid
            GlyphSelectionError: If glyph selection is invalid
        """
        batch_start_time = time.time()
        
        logger.info("Starting batch glyph duplication...")
        
        # Get font and glyphs
        font = self.get_current_font()
        selected_glyphs = self.get_selected_glyphs()
        
        logger.info(f"Font: {font.info.familyName}")
        logger.info(f"Selected glyphs: {len(selected_glyphs)}")
        
        # Process each glyph
        successful_results = []
        failed_results = []
        
        for i, glyph in enumerate(selected_glyphs, 1):
            if self.config.show_progress:
                logger.info(f"Processing {i}/{len(selected_glyphs)}: {glyph.name}")
            
            result = self.process_single_glyph(font, glyph)
            
            if result.success:
                successful_results.append(result)
            else:
                failed_results.append(result)
        
        # Update font if any changes were made
        if successful_results:
            try:
                font.changed()
            except Exception as e:
                logger.warning(f"Failed to mark font as changed: {e}")
        
        # Calculate total time
        total_time = time.time() - batch_start_time
        
        # Create result
        batch_result = BatchResult(
            total_processed=len(selected_glyphs),
            successful=successful_results,
            failed=failed_results,
            total_time=total_time
        )
        
        # Log comprehensive results
        self._log_batch_results(batch_result)
        
        return batch_result
    
    def _log_batch_results(self, result: BatchResult) -> None:
        """Log comprehensive batch processing results."""
        logger.info("=" * 60)
        logger.info("BATCH PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total processed: {result.total_processed}")
        logger.info(f"Successful: {len(result.successful)}")
        logger.info(f"Failed: {len(result.failed)}")
        logger.info(f"Success rate: {result.success_rate:.1f}%")
        logger.info(f"Total time: {result.total_time:.2f}s")
        
        if result.successful:
            avg_time = sum(r.processing_time for r in result.successful) / len(result.successful)
            logger.info(f"Average processing time: {avg_time:.3f}s")
            
            logger.info("\nCreated alternates:")
            for r in result.successful:
                logger.info(f"  ✓ {r.glyph_name} → {r.alternate_name}")
        
        if result.failed:
            logger.warning("\nFailed glyphs:")
            for r in result.failed:
                logger.warning(f"  ✗ {r.glyph_name}: {r.error_message}")
        
        logger.info("=" * 60)

class KeyboardSubscriber(Subscriber):
    """Professional keyboard subscriber with robust error handling and cleanup."""
    
    debug = True
    
    def __init__(self, config: ProcessingConfig = None):
        """Initialize subscriber with processor configuration."""
        super().__init__()
        self.processor = DuplicateGlyphProcessor(config)
        self._register_cleanup()
        logger.info("Keyboard subscriber initialized")
    
    def _register_cleanup(self) -> None:
        """Register this subscriber for cleanup tracking."""
        global _active_subscribers
        _active_subscribers.add(weakref.ref(self, self._cleanup_callback))
    
    @staticmethod
    def _cleanup_callback(ref: weakref.ReferenceType) -> None:
        """Callback for subscriber cleanup."""
        global _active_subscribers
        _active_subscribers.discard(ref)
    
    def build(self) -> None:
        """Build subscriber (required by Subscriber protocol)."""
        pass
    
    def destroy(self) -> None:
        """Properly destroy subscriber and clean up resources."""
        try:
            super().destroy()
        except:
            pass
        logger.info("Keyboard subscriber destroyed")
    
    def keyDown(self, info: Dict[str, Any]) -> None:
        """Handle keyboard events with comprehensive error handling.
        
        Args:
            info: Event information dictionary
        """
        try:
            logger.debug(f"KeyDown event received: {info}")
            
            # Validate event info
            if not isinstance(info, dict):
                logger.debug("Invalid event info - not a dict")
                return
            
            key_char = info.get('characters', '')
            if not key_char:
                logger.debug("No characters in event info")
                return
            
            logger.debug(f"Key character: '{key_char}', event info: {info}")
            
            # Check for Command+D
            is_d_key = key_char.lower() == 'd'
            is_command_down = info.get('commandDown', False)
            
            logger.debug(f"Is D key: {is_d_key}, Command down: {is_command_down}")
            
            if is_d_key and is_command_down:
                logger.info("🎯 Command+D detected - processing glyphs...")
                
                try:
                    result = self.processor.process_batch()
                    
                    if result.total_processed > 0:
                        success_msg = f"✅ Processed {result.total_processed} glyphs - {len(result.successful)} successful, {len(result.failed)} failed"
                        logger.info(success_msg)
                        print(success_msg)  # Also print to console
                    else:
                        logger.info("No glyphs were processed")
                    
                except Exception as e:
                    logger.error(f"Batch processing failed: {e}")
                    print(f"Error: {e}")
            else:
                logger.debug(f"Key combination not matched: {key_char} + cmd={is_command_down}")
                    
        except Exception as e:
            logger.error(f"Error in keyboard handler: {e}")
            print(f"Keyboard handler error: {e}")

# Global subscriber instance
_global_subscriber: Optional[KeyboardSubscriber] = None

def run_duplicate_now(config: ProcessingConfig = None, show_output: bool = False) -> BatchResult:
    """Run duplication immediately with given configuration.
    
    Args:
        config: Processing configuration, uses defaults if None
        show_output: Whether to show the output window
        
    Returns:
        BatchResult with operation details
        
    Raises:
        DuplicateGlyphError: If operation fails
    """
    print("🚀 Running duplicate now...")
    
    # Initialize output window only if requested
    if show_output:
        output = OutputWindow()
        output.clear()
        output.show()
    
    # Create processor and run
    processor = DuplicateGlyphProcessor(config)
    result = processor.process_batch()
    
    print(f"📊 Result: {result.total_processed} processed, {len(result.successful)} successful")
    return result

def test_duplication():
    """Test function to run duplication immediately."""
    print("🧪 Testing duplication functionality...")
    try:
        config = ProcessingConfig(
            suffix_pattern="ss",
            start_number=1,
            apply_color=True,
            color=(0.6, 0.6, 0.6, 0.7),
            show_progress=True
        )
        result = run_duplicate_now(config, show_output=True)
        print(f"✅ Test completed: {result.total_processed} glyphs processed")
        return result
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

def setup_keyboard_shortcut(config: ProcessingConfig = None) -> None:
    """Set up Command+D keyboard shortcut with proper cleanup and registration.
    
    Args:
        config: Processing configuration, uses defaults if None
    """
    global _global_subscriber
    
    # Clean up existing subscriber
    cleanup_keyboard_shortcut()
    
    # Create new subscriber
    _global_subscriber = KeyboardSubscriber(config)
    
    # Register the subscriber with RoboFont
    try:
        registerGlyphEditorSubscriber(_global_subscriber)
        logger.info("✓ Subscriber registered with RoboFont")
    except Exception as e:
        logger.error(f"Failed to register subscriber: {e}")
    
    logger.info("✓ Command+D shortcut installed")
    logger.info("✓ Select one or more glyphs and press Command+D to duplicate as stylistic alternates")

def cleanup_keyboard_shortcut() -> None:
    """Clean up keyboard shortcut subscriber with proper unregistration."""
    global _global_subscriber
    
    if _global_subscriber:
        try:
            unregisterGlyphEditorSubscriber(_global_subscriber)
            logger.info("✓ Subscriber unregistered from RoboFont")
        except Exception as e:
            logger.warning(f"Error unregistering subscriber: {e}")
        
        _global_subscriber.destroy()
        _global_subscriber = None
    
    # Clean up any orphaned subscribers
    global _active_subscribers
    dead_refs = [ref for ref in _active_subscribers if ref() is None]
    for ref in dead_refs:
        _active_subscribers.discard(ref)
    
    logger.info("Keyboard shortcut cleaned up")

# Main execution
if __name__ == '__main__':
    try:
        # Create professional configuration
        config = ProcessingConfig(
            suffix_pattern="ss",
            start_number=1,
            apply_color=True,
            color=(0.6, 0.6, 0.6, 0.7),  # Slightly more visible grey
            copy_components=True,
            copy_anchors=True,
            position_after_original=True,
            show_progress=True,
            validate_compatibility=True
        )
        
        print("=" * 60)
        print("997 DUPLICATE GLYPH v3.0 - PROFESSIONAL EDITION")
        print("=" * 60)
        
        logger.info("=" * 60)
        logger.info("997 DUPLICATE GLYPH v3.0 - PROFESSIONAL EDITION")
        logger.info("=" * 60)
        
        # First run test to see if basic functionality works
        print("🧪 Testing basic functionality...")
        try:
            result = test_duplication()
            if result and result.total_processed > 0:
                print(f"✅ Test passed - processed {result.total_processed} glyphs")
            else:
                print("⚠️ Test completed but no glyphs were processed")
        except (FontContextError, GlyphSelectionError) as e:
            print(f"ℹ️ No glyphs selected for test: {e}")
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        # Then set up keyboard shortcut
        print("\n🔧 Setting up keyboard shortcut...")
        setup_keyboard_shortcut(config)
        
        print("✨ Script ready! Select glyphs and press Command+D")
        logger.info("Script ready! ✨")
        
    except Exception as e:
        logger.error(f"Script initialization failed: {e}")
        print(f"Fatal error: {e}") 