# MRL Glyph Dimensions Controller
# Developed by Kevin Kuhn (Mining Raw Letters)

"""
MRL Glyph Dimensions Extension

A comprehensive RoboFont extension for managing glyph dimensions including:
- Horizontal metrics: sidebearings, width
- Vertical metrics: ascender, descender, cap height, x-height, units per em
- Batch operations on multiple glyphs
- Real-time display of current font metrics

Follows functional/declarative programming paradigm with proper error handling.
"""

from typing import Optional, List, Tuple, Dict, Any
import logging
from vanilla import *
import AppKit

# RoboFont and FontParts imports
try:
    from mojo.roboFont import CurrentFont, AllFonts, CurrentGlyph
    from mojo.UI import Message
    from defcon import Font
    from fontParts.world import RFont
    from mojo.events import addObserver, removeObserver
    import time
except ImportError as import_error:
    logging.error(f"Required RoboFont modules not available: {import_error}")
    raise

# Import utility functions
from mrl_glyph_dimensions_utils import (
    validate_current_font,
    apply_glyph_horizontal_metrics,
    apply_vertical_metrics,
    apply_webfont_strategy,
    get_font_metrics_summary,
    get_glyph_metrics,
    validate_metric_value
)


class MRL_GlyphDimensionsController:
    """
    Main controller for the MRL Glyph Dimensions extension.
    Provides a comprehensive UI for managing glyph dimensions.
    """
    
    def __init__(self):
        """Initialize the controller and create the main window."""
        self.font = CurrentFont()
        self.selected_glyphs = []
        self.observers_added = False
        self.last_selection_hash = None
        
        # Create the main window
        self.create_main_window()
        
        # Add observers for font and glyph changes
        self.add_observers()
        
        # Initial update of the UI
        self.update_ui()
        
        # Start periodic refresh
        self.start_periodic_refresh()
    
    def create_main_window(self):
        """Create the main window with all UI elements."""
        self.w = Window(
            (400, 470),
            "MRL Glyph Dimensions",
            minSize=(400, 470),
            maxSize=(600, 600)
        )
        
        # Main container
        self.w.main_container = Group((10, 10, -10, -10))
        
        # Font info section
        self.w.main_container.font_info_group = Group((0, 0, -0, 80))
        self.w.main_container.font_info_group.title = TextBox((0, 0, -0, 20), "Font Information", sizeStyle="small")
        self.w.main_container.font_info_group.font_name = TextBox((0, 25, -0, 20), "No font open", sizeStyle="small")
        self.w.main_container.font_info_group.glyph_count = TextBox((0, 50, -0, 20), "Glyphs: 0", sizeStyle="small")
        self.w.main_container.font_info_group.selected_glyphs = TextBox((0, 75, -0, 20), "Selected glyphs: None", sizeStyle="small")
        
        # Horizontal metrics section
        self.w.main_container.horizontal_group = Group((0, 90, -0, 100))
        self.w.main_container.horizontal_group.title = TextBox((0, 0, -0, 20), "Horizontal Metrics", sizeStyle="small")
        
        # Width controls
        self.w.main_container.horizontal_group.width_label = TextBox((0, 25, 80, 20), "Width:", sizeStyle="small")
        self.w.main_container.horizontal_group.width_value = EditText((85, 23, 80, 24), "0")
        self.w.main_container.horizontal_group.width_apply = Button((170, 23, 60, 24), "Apply", callback=self.apply_width)
        
        # Left sidebearing controls
        self.w.main_container.horizontal_group.left_label = TextBox((0, 55, 80, 20), "Left SB:", sizeStyle="small")
        self.w.main_container.horizontal_group.left_value = EditText((85, 53, 80, 24), "0")
        self.w.main_container.horizontal_group.left_apply = Button((170, 53, 60, 24), "Apply", callback=self.apply_left_sidebearing)
        
        # Right sidebearing controls
        self.w.main_container.horizontal_group.right_label = TextBox((0, 85, 80, 20), "Right SB:", sizeStyle="small")
        self.w.main_container.horizontal_group.right_value = EditText((85, 83, 80, 24), "0")
        self.w.main_container.horizontal_group.right_apply = Button((170, 83, 60, 24), "Apply", callback=self.apply_right_sidebearing)
        
        # Vertical metrics section
        self.w.main_container.vertical_group = Group((0, 200, -0, 200))
        self.w.main_container.vertical_group.title = TextBox((0, 0, -0, 20), "Vertical Metrics", sizeStyle="small")
        
        # Units per em
        self.w.main_container.vertical_group.upem_label = TextBox((0, 25, 80, 20), "Units/Em:", sizeStyle="small")
        self.w.main_container.vertical_group.upem_value = EditText((85, 23, 80, 24), "1000")
        self.w.main_container.vertical_group.upem_apply = Button((170, 23, 60, 24), "Apply", callback=self.apply_units_per_em)
        
        # Ascender
        self.w.main_container.vertical_group.ascender_label = TextBox((0, 55, 80, 20), "Ascender:", sizeStyle="small")
        self.w.main_container.vertical_group.ascender_value = EditText((85, 53, 80, 24), "750")
        self.w.main_container.vertical_group.ascender_apply = Button((170, 53, 60, 24), "Apply", callback=self.apply_ascender)
        
        # Cap height
        self.w.main_container.vertical_group.cap_label = TextBox((0, 85, 80, 20), "Cap Height:", sizeStyle="small")
        self.w.main_container.vertical_group.cap_value = EditText((85, 83, 80, 24), "700")
        self.w.main_container.vertical_group.cap_apply = Button((170, 83, 60, 24), "Apply", callback=self.apply_cap_height)
        
        # X-height
        self.w.main_container.vertical_group.xheight_label = TextBox((0, 115, 80, 20), "X-Height:", sizeStyle="small")
        self.w.main_container.vertical_group.xheight_value = EditText((85, 113, 80, 24), "500")
        self.w.main_container.vertical_group.xheight_apply = Button((170, 113, 60, 24), "Apply", callback=self.apply_x_height)
        
        # Descender
        self.w.main_container.vertical_group.descender_label = TextBox((0, 145, 80, 20), "Descender:", sizeStyle="small")
        self.w.main_container.vertical_group.descender_value = EditText((85, 143, 80, 24), "-250")
        self.w.main_container.vertical_group.descender_apply = Button((170, 143, 60, 24), "Apply", callback=self.apply_descender)
        
        # Webfont strategy
        self.w.main_container.vertical_group.webfont_apply = Button((85, 175, 145, 30), "Apply Webfont", callback=self.apply_webfont_strategy)
        self.w.main_container.vertical_group.webfont_check = Button((85, 210, 145, 25), "Check Webfont", callback=self.check_webfont_status)
        
        # Status section
        self.w.main_container.status_group = Group((0, 410, -0, 30))
        self.w.main_container.status_group.status = TextBox((0, 0, -0, 25), "Ready", sizeStyle="small")
        
        # Open the window
        self.w.open()
    
    def add_observers(self):
        """Add observers for font and glyph changes."""
        if not self.observers_added:
            addObserver(self, "fontDidOpen", "fontDidOpen")
            addObserver(self, "fontDidClose", "fontDidClose")
            addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
            addObserver(self, "glyphDidChange", "glyphDidChange")
            self.observers_added = True
    
    def remove_observers(self):
        """Remove observers when closing."""
        if self.observers_added:
            removeObserver(self, "fontDidOpen")
            removeObserver(self, "fontDidClose")
            removeObserver(self, "currentGlyphChanged")
            removeObserver(self, "glyphDidChange")
            self.observers_added = False
    
    def update_ui(self):
        """Update the UI with current font and glyph information."""
        self.font = CurrentFont()
        
        if self.font:
            # Update font info
            font_name = f"{self.font.info.familyName} {self.font.info.styleName}"
            self.w.main_container.font_info_group.font_name.set(font_name)
            self.w.main_container.font_info_group.glyph_count.set(f"Glyphs: {len(self.font)}")
            
            # Update selected glyphs info
            self.selected_glyphs = self.get_selected_glyphs()
            
            if self.selected_glyphs:
                glyph_names = [glyph.name for glyph in self.selected_glyphs]
                if len(glyph_names) == 1:
                    selection_text = f"Selected glyph: {glyph_names[0]}"
                else:
                    selection_text = f"Selected glyphs: {len(glyph_names)} glyphs"
                
                self.w.main_container.font_info_group.selected_glyphs.set(selection_text)
                
                # Analyze dimensions
                dimensions = self.analyze_glyph_dimensions(self.selected_glyphs)
                
                # Update horizontal metrics fields
                if dimensions['width']['uniform']:
                    self.w.main_container.horizontal_group.width_value.set(str(dimensions['width']['value']))
                else:
                    self.w.main_container.horizontal_group.width_value.set("")
                
                if dimensions['left_margin']['uniform']:
                    self.w.main_container.horizontal_group.left_value.set(str(dimensions['left_margin']['value']))
                else:
                    self.w.main_container.horizontal_group.left_value.set("")
                
                if dimensions['right_margin']['uniform']:
                    self.w.main_container.horizontal_group.right_value.set(str(dimensions['right_margin']['value']))
                else:
                    self.w.main_container.horizontal_group.right_value.set("")
                
                # Update selection info
                info_parts = []
                if dimensions['width']['uniform']:
                    info_parts.append(f"W:{dimensions['width']['value']}")
                if dimensions['left_margin']['uniform']:
                    info_parts.append(f"L:{dimensions['left_margin']['value']}")
                if dimensions['right_margin']['uniform']:
                    info_parts.append(f"R:{dimensions['right_margin']['value']}")
                
                if info_parts:
                    self.w.main_container.font_info_group.selected_glyphs.set(f"Selected glyph: {glyph_names[0]} - Uniform: {', '.join(info_parts)}")
                else:
                    self.w.main_container.font_info_group.selected_glyphs.set(f"Selected glyph: {glyph_names[0]} - Mixed dimensions")
            else:
                self.w.main_container.font_info_group.selected_glyphs.set("Selected glyphs: None")
                
                # Clear horizontal metrics fields
                self.w.main_container.horizontal_group.width_value.set("")
                self.w.main_container.horizontal_group.left_value.set("")
                self.w.main_container.horizontal_group.right_value.set("")
            
            # Update vertical metrics
            self.w.main_container.vertical_group.upem_value.set(str(self.font.info.unitsPerEm))
            self.w.main_container.vertical_group.ascender_value.set(str(self.font.info.ascender))
            self.w.main_container.vertical_group.cap_value.set(str(self.font.info.capHeight))
            self.w.main_container.vertical_group.xheight_value.set(str(self.font.info.xHeight))
            self.w.main_container.vertical_group.descender_value.set(str(self.font.info.descender))
        else:
            # No font open
            self.w.main_container.font_info_group.font_name.set("No font open")
            self.w.main_container.font_info_group.glyph_count.set("Glyphs: 0")
            self.w.main_container.font_info_group.selected_glyphs.set("Selected glyphs: None")
            self.w.main_container.font_info_group.selection_info.set("Selection info: ")
            
            # Clear horizontal metrics fields
            self.w.main_container.horizontal_group.width_value.set("")
            self.w.main_container.horizontal_group.left_value.set("")
            self.w.main_container.horizontal_group.right_value.set("")
    
    def validate_font(self) -> bool:
        """Validate that a font is open."""
        try:
            self.font = validate_current_font()
            return True
        except RuntimeError:
            Message("No font is currently open. Please open a font first.")
            return False
    
    def get_selected_glyphs(self) -> List:
        """Get list of currently selected glyphs."""
        if not self.font:
            return []
        
        try:
            # Try different methods to get selected glyphs
            selected_glyphs = []
            
            # Method 1: Try getSelectedGlyphNames()
            try:
                selected_names = self.font.getSelectedGlyphNames()
                for name in selected_names:
                    if name in self.font:
                        selected_glyphs.append(self.font[name])
            except AttributeError:
                pass
            
            # Method 2: If no selection found, try CurrentGlyph()
            if not selected_glyphs:
                try:
                    current_glyph = CurrentGlyph()
                    if current_glyph:
                        selected_glyphs.append(current_glyph)
                except:
                    pass
            
            # Method 3: Try to get selection from font window
            if not selected_glyphs:
                try:
                    # Try to access the font window's selection
                    if hasattr(self.font, 'getSelectedGlyphs'):
                        selected_glyphs = self.font.getSelectedGlyphs()
                    elif hasattr(self.font, 'selectedGlyphs'):
                        selected_glyphs = self.font.selectedGlyphs
                except:
                    pass
            
            # Method 4: Try to access the font window directly
            if not selected_glyphs:
                try:
                    # Try to get the current font window
                    from mojo.UI import CurrentFontWindow
                    font_window = CurrentFontWindow()
                    if font_window:
                        # Try different ways to get selection from the window
                        if hasattr(font_window, 'getSelectedGlyphNames'):
                            selected_names = font_window.getSelectedGlyphNames()
                            for name in selected_names:
                                if name in self.font:
                                    selected_glyphs.append(self.font[name])
                        elif hasattr(font_window, 'selectedGlyphNames'):
                            selected_names = font_window.selectedGlyphNames
                            for name in selected_names:
                                if name in self.font:
                                    selected_glyphs.append(self.font[name])
                except:
                    pass
            
            return selected_glyphs
            
        except Exception as e:
            logging.error(f"Error getting selected glyphs: {e}")
            return []
    
    def analyze_glyph_dimensions(self, glyphs: List) -> Dict[str, Any]:
        """
        Analyze dimensions of selected glyphs.
        Returns a dictionary with dimension values and whether they're uniform.
        """
        if not glyphs:
            return {
                'width': {'value': None, 'uniform': False},
                'left_margin': {'value': None, 'uniform': False},
                'right_margin': {'value': None, 'uniform': False}
            }
        
        # Get all dimension values
        widths = []
        left_margins = []
        right_margins = []
        
        for glyph in glyphs:
            if hasattr(glyph, 'width') and glyph.width is not None:
                widths.append(glyph.width)
            if hasattr(glyph, 'leftMargin') and glyph.leftMargin is not None:
                left_margins.append(glyph.leftMargin)
            if hasattr(glyph, 'rightMargin') and glyph.rightMargin is not None:
                right_margins.append(glyph.rightMargin)
        
        # Check if dimensions are uniform
        width_uniform = len(set(widths)) == 1 if widths else False
        left_uniform = len(set(left_margins)) == 1 if left_margins else False
        right_uniform = len(set(right_margins)) == 1 if right_margins else False
        
        return {
            'width': {'value': widths[0] if width_uniform else None, 'uniform': width_uniform},
            'left_margin': {'value': left_margins[0] if left_uniform else None, 'uniform': left_uniform},
            'right_margin': {'value': right_margins[0] if right_uniform else None, 'uniform': right_uniform}
        }
    
    def validate_glyph_selection(self) -> bool:
        """Validate that at least one glyph is selected."""
        if not self.selected_glyphs:
            Message("No glyphs are currently selected. Please select one or more glyphs first.")
            return False
        return True
    
    def refresh_selection(self, sender):
        """Refresh the glyph selection and update the UI."""
        try:
            self.update_ui()
            self.update_status("Selection refreshed")
        except Exception as e:
            self.update_status(f"Error refreshing selection: {e}")
            logging.error(f"Error in refresh_selection: {e}")
    
    def get_selection_hash(self) -> str:
        """Get a hash of the current selection for change detection."""
        if not self.font:
            return ""
        
        try:
            selected_glyphs = self.get_selected_glyphs()
            if not selected_glyphs:
                return "none"
            
            # Create a hash based on glyph names
            names = sorted([glyph.name for glyph in selected_glyphs])
            return ",".join(names)
        except Exception as e:
            logging.error(f"Error getting selection hash: {e}")
            return ""
    
    def start_periodic_refresh(self):
        """Start periodic refresh to check for selection changes."""
        # For now, we'll rely on the observer pattern and manual refresh
        # The periodic refresh was causing issues with Vanilla Window
        pass
    
    def debug_selection(self, sender):
        """Debug the current selection detection."""
        try:
            debug_info = []
            
            # Check font
            if self.font:
                debug_info.append(f"Font: {self.font.info.familyName}")
            else:
                debug_info.append("Font: None")
            
            # Try different selection methods
            debug_info.append("\n--- Selection Methods ---")
            
            # Method 1: getSelectedGlyphNames
            try:
                if hasattr(self.font, 'getSelectedGlyphNames'):
                    names = self.font.getSelectedGlyphNames()
                    debug_info.append(f"getSelectedGlyphNames: {names}")
                else:
                    debug_info.append("getSelectedGlyphNames: Not available")
            except Exception as e:
                debug_info.append(f"getSelectedGlyphNames: Error - {e}")
            
            # Method 2: CurrentGlyph
            try:
                current = CurrentGlyph()
                if current:
                    debug_info.append(f"CurrentGlyph: {current.name}")
                else:
                    debug_info.append("CurrentGlyph: None")
            except Exception as e:
                debug_info.append(f"CurrentGlyph: Error - {e}")
            
            # Method 3: Font window
            try:
                from mojo.UI import CurrentFontWindow
                font_window = CurrentFontWindow()
                if font_window:
                    debug_info.append(f"FontWindow: {type(font_window)}")
                    if hasattr(font_window, 'getSelectedGlyphNames'):
                        names = font_window.getSelectedGlyphNames()
                        debug_info.append(f"FontWindow.getSelectedGlyphNames: {names}")
                    else:
                        debug_info.append("FontWindow.getSelectedGlyphNames: Not available")
                else:
                    debug_info.append("FontWindow: None")
            except Exception as e:
                debug_info.append(f"FontWindow: Error - {e}")
            
            # Current selection
            current_selection = self.get_selected_glyphs()
            debug_info.append(f"\nCurrent selection: {[g.name for g in current_selection]}")
            
            # Show debug info
            debug_text = "\n".join(debug_info)
            Message(debug_text)
            
        except Exception as e:
            Message(f"Debug error: {e}")
            logging.error(f"Error in debug_selection: {e}")
    
    def get_int_value(self, text_field) -> Optional[int]:
        """Get integer value from text field."""
        return validate_metric_value(text_field.get())
    
    # Horizontal metrics methods
    def apply_width(self, sender):
        """Apply width to selected glyphs."""
        if not self.validate_glyph_selection():
            return
        
        width = self.get_int_value(self.w.main_container.horizontal_group.width_value)
        if width is not None:
            try:
                applied_count = 0
                for glyph in self.selected_glyphs:
                    glyph.width = width
                    glyph.update()
                    applied_count += 1
                
                self.font.changed()
                self.update_status(f"Applied width {width} to {applied_count} glyphs")
                self.update_ui()  # Refresh the UI
            except Exception as e:
                self.update_status(f"Error applying width: {e}")
    
    def apply_left_sidebearing(self, sender):
        """Apply left sidebearing to selected glyphs."""
        if not self.validate_glyph_selection():
            return
        
        left_sb = self.get_int_value(self.w.main_container.horizontal_group.left_value)
        if left_sb is not None:
            try:
                applied_count = 0
                for glyph in self.selected_glyphs:
                    glyph.leftMargin = left_sb
                    glyph.update()
                    applied_count += 1
                
                self.font.changed()
                self.update_status(f"Applied left sidebearing {left_sb} to {applied_count} glyphs")
                self.update_ui()  # Refresh the UI
            except Exception as e:
                self.update_status(f"Error applying left sidebearing: {e}")
    
    def apply_right_sidebearing(self, sender):
        """Apply right sidebearing to selected glyphs."""
        if not self.validate_glyph_selection():
            return
        
        right_sb = self.get_int_value(self.w.main_container.horizontal_group.right_value)
        if right_sb is not None:
            try:
                applied_count = 0
                for glyph in self.selected_glyphs:
                    glyph.rightMargin = right_sb
                    glyph.update()
                    applied_count += 1
                
                self.font.changed()
                self.update_status(f"Applied right sidebearing {right_sb} to {applied_count} glyphs")
                self.update_ui()  # Refresh the UI
            except Exception as e:
                self.update_status(f"Error applying right sidebearing: {e}")
    

    
    # Vertical metrics methods
    def apply_units_per_em(self, sender):
        """Apply units per em to font."""
        if not self.validate_font():
            return
        
        upem = self.get_int_value(self.w.main_container.vertical_group.upem_value)
        if upem is not None:
            self.font.info.unitsPerEm = upem
            self.font.changed()
            self.update_status(f"Applied units per em: {upem}")
    
    def apply_ascender(self, sender):
        """Apply ascender to font."""
        if not self.validate_font():
            return
        
        ascender = self.get_int_value(self.w.main_container.vertical_group.ascender_value)
        if ascender is not None:
            self.font.info.ascender = ascender
            self.font.changed()
            self.update_status(f"Applied ascender: {ascender}")
    
    def apply_cap_height(self, sender):
        """Apply cap height to font."""
        if not self.validate_font():
            return
        
        cap_height = self.get_int_value(self.w.main_container.vertical_group.cap_value)
        if cap_height is not None:
            self.font.info.capHeight = cap_height
            self.font.changed()
            self.update_status(f"Applied cap height: {cap_height}")
    
    def apply_x_height(self, sender):
        """Apply x-height to font."""
        if not self.validate_font():
            return
        
        x_height = self.get_int_value(self.w.main_container.vertical_group.xheight_value)
        if x_height is not None:
            self.font.info.xHeight = x_height
            self.font.changed()
            self.update_status(f"Applied x-height: {x_height}")
    
    def apply_descender(self, sender):
        """Apply descender to font."""
        if not self.validate_font():
            return
        
        descender = self.get_int_value(self.w.main_container.vertical_group.descender_value)
        if descender is not None:
            self.font.info.descender = descender
            self.font.changed()
            self.update_status(f"Applied descender: {descender}")
    
    def apply_webfont_strategy(self, sender):
        """Apply webfont strategy for cross-platform consistency."""
        if not self.validate_font():
            return
        
        # Get values from UI
        upem = self.get_int_value(self.w.main_container.vertical_group.upem_value)
        ascender = self.get_int_value(self.w.main_container.vertical_group.ascender_value)
        descender = self.get_int_value(self.w.main_container.vertical_group.descender_value)
        cap_height = self.get_int_value(self.w.main_container.vertical_group.cap_value)
        x_height = self.get_int_value(self.w.main_container.vertical_group.xheight_value)
        
        if any(v is None for v in [upem, ascender, descender, cap_height, x_height]):
            return
        
        # Create metrics dictionary
        metrics = {
            'units_per_em': upem,
            'ascender': ascender,
            'descender': descender,
            'cap_height': cap_height,
            'x_height': x_height
        }
        
        # Apply webfont strategy using utility function
        if apply_webfont_strategy(self.font, metrics):
            self.update_status("Applied webfont strategy successfully")
        else:
            self.update_status("Failed to apply webfont strategy")
    
    def check_webfont_status(self, sender):
        """Check the current webfont metrics status."""
        if not self.validate_font():
            return
        
        try:
            # Get current metrics
            info = self.font.info
            
            # Check if webfont metrics are set
            webfont_metrics = {
                'sTypoAscender': getattr(info, 'openTypeOS2TypoAscender', None),
                'sTypoDescender': getattr(info, 'openTypeOS2TypoDescender', None),
                'sTypoLineGap': getattr(info, 'openTypeOS2TypoLineGap', None),
                'hheaAscent': getattr(info, 'openTypeHheaAscent', None),
                'hheaDescent': getattr(info, 'openTypeHheaDescent', None),
                'hheaLineGap': getattr(info, 'openTypeHheaLineGap', None),
                'usWinAscent': getattr(info, 'openTypeOS2WinAscent', None),
                'usWinDescent': getattr(info, 'openTypeOS2WinDescent', None),
                'useTypoMetrics': getattr(info, 'openTypeOS2UseTypoMetrics', None)
            }
            
            # Create status message
            status_parts = []
            for metric, value in webfont_metrics.items():
                if value is not None:
                    status_parts.append(f"{metric}: {value}")
                else:
                    status_parts.append(f"{metric}: Not set")
            
            status_text = " | ".join(status_parts)
            self.update_status(f"Webfont Status: {status_text}")
            
        except Exception as e:
            self.update_status(f"Error checking webfont status: {e}")
            logging.error(f"Error in check_webfont_status: {e}")
    

    
    def update_status(self, message: str):
        """Update the status message."""
        self.w.main_container.status_group.status.set(message)
    
    # Observer methods
    def fontDidOpen(self, notification):
        """Handle font open event."""
        try:
            self.update_ui()
        except Exception as e:
            logging.error(f"Error in fontDidOpen: {e}")
    
    def fontDidClose(self, notification):
        """Handle font close event."""
        try:
            self.update_ui()
        except Exception as e:
            logging.error(f"Error in fontDidClose: {e}")
    
    def currentGlyphChanged(self, notification):
        """Handle current glyph change event."""
        try:
            self.update_ui()
        except Exception as e:
            logging.error(f"Error in currentGlyphChanged: {e}")
    
    def glyphDidChange(self, notification):
        """Handle glyph change event."""
        try:
            self.update_ui()
        except Exception as e:
            logging.error(f"Error in glyphDidChange: {e}")
    
    def __del__(self):
        """Cleanup when the controller is destroyed."""
        self.remove_observers() 