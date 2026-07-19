# MRL Duplicate Layers
# Developed by Kevin Kuhn (Mining Raw Letters)
# 
# Simple script to duplicate layers and metrics for multiple selected glyphs

from mojo.roboFont import CurrentFont, CurrentGlyph
from vanilla import Window, Group, TextBox, Button, PopUpButton, EditText, CheckBox
import math

class MRLDuplicateLayers:
    def __init__(self):
        self.font = CurrentFont()
        self.selected_glyphs = []
        self.create_ui()
        
    def create_ui(self):
        self.w = Window((350, 450), "Duplicate Layers & Metrics")
        
        # Glyph selection
        self.w.glyph_group = Group((10, 10, -10, 80))
        self.w.glyph_group.title = TextBox((0, 0, -0, 20), "Layers")
        self.w.glyph_group.add_field = EditText((0, 25, 180, 24), "")
        self.w.glyph_group.add_button = Button((190, 25, 60, 24), "Add", callback=self.add_glyph)
        self.w.glyph_group.get_selected_button = Button((0, 55, 100, 24), "Get Selected", callback=self.get_selected)
        self.w.glyph_group.select_all_button = Button((110, 55, 100, 24), "Select All", callback=self.select_all)
        self.w.glyph_group.count_label = TextBox((220, 55, -0, 20), "(0) selected glyphs")
        
        # Layer selection
        self.w.layer_group = Group((10, 100, -10, 80))
        self.w.layer_group.title = TextBox((0, 0, -0, 20), "Layer")
        self.w.layer_group.source_label = TextBox((0, 25, 60, 20), "From:")
        self.w.layer_group.source_popup = PopUpButton((65, 23, 150, 24), ["foreground"])
        self.w.layer_group.target_label = TextBox((0, 55, 60, 20), "To:")
        self.w.layer_group.target_field = EditText((65, 53, 150, 24), "duplicate")
        
        # Metrics duplication
        self.w.metrics_group = Group((10, 190, -10, 60))
        self.w.metrics_group.title = TextBox((0, 0, -0, 20), "Metrics")
        self.w.metrics_group.duplicate_metrics = CheckBox((0, 25, 150, 20), "Duplicate Metrics", value=True)
        self.w.metrics_group.metrics_info = TextBox((160, 25, -0, 20), "(width, sidebearings)")
        
        # Transformations
        self.w.transform_group = Group((10, 260, -10, 120))
        self.w.transform_group.title = TextBox((0, 0, -0, 20), "Transform")
        self.w.transform_group.flip_h = CheckBox((0, 25, 100, 20), "Flip H")
        self.w.transform_group.flip_v = CheckBox((110, 25, 100, 20), "Flip V")
        self.w.transform_group.rotate_label = TextBox((0, 55, 60, 20), "Rotate:")
        self.w.transform_group.rotate_field = EditText((65, 53, 60, 24), "0")
        self.w.transform_group.scale_label = TextBox((0, 85, 60, 20), "Scale:")
        self.w.transform_group.scale_field = EditText((65, 83, 60, 24), "100")
        
        # Action
        self.w.action_group = Group((10, 390, -10, 50))
        self.w.action_group.duplicate_button = Button((0, 0, 100, 30), "Duplicate", callback=self.duplicate)
        self.w.action_group.status_label = TextBox((110, 5, -0, 20), "Ready")
        
        self.w.open()
        self.update_layers(None)
        
    def add_glyph(self, sender):
        name = self.w.glyph_group.add_field.get().strip()
        if name and self.font and name in self.font:
            if name not in self.selected_glyphs:
                self.selected_glyphs.append(name)
                self.update_count()
                self.w.glyph_group.add_field.set("")
                self.w.action_group.status_label.set(f"Added: {name}")
            else:
                self.w.action_group.status_label.set(f"Already selected: {name}")
        else:
            self.w.action_group.status_label.set("Invalid glyph name")
    
    def get_selected(self, sender):
        """Get glyphs selected in RoboFont using proven method from MRL_Glyph_Dimensions."""
        if not self.font:
            self.w.action_group.status_label.set("No font open")
            return
            
        selected_names = []
        
        try:
            # Method 1: Try getSelectedGlyphNames() (most reliable)
            try:
                selected_names = self.font.getSelectedGlyphNames()
                if selected_names:
                    print(f"Method 1 (getSelectedGlyphNames) found: {selected_names}")
            except AttributeError:
                print("Method 1: getSelectedGlyphNames not available")
            except Exception as e:
                print(f"Method 1 failed: {e}")
            
            # Method 2: Try to get selection from font window
            if not selected_names:
                try:
                    if hasattr(self.font, 'getSelectedGlyphs'):
                        selected_glyphs = self.font.getSelectedGlyphs()
                        selected_names = [g.name for g in selected_glyphs]
                        print(f"Method 2 (getSelectedGlyphs) found: {selected_names}")
                    elif hasattr(self.font, 'selectedGlyphs'):
                        selected_glyphs = self.font.selectedGlyphs
                        selected_names = [g.name for g in selected_glyphs]
                        print(f"Method 2 (selectedGlyphs) found: {selected_names}")
                except Exception as e:
                    print(f"Method 2 failed: {e}")
            
            # Method 3: Try to access the font window directly
            if not selected_names:
                try:
                    from mojo.UI import CurrentFontWindow
                    font_window = CurrentFontWindow()
                    if font_window:
                        if hasattr(font_window, 'getSelectedGlyphNames'):
                            selected_names = font_window.getSelectedGlyphNames()
                            print(f"Method 3 (CurrentFontWindow.getSelectedGlyphNames) found: {selected_names}")
                        elif hasattr(font_window, 'selectedGlyphNames'):
                            selected_names = font_window.selectedGlyphNames
                            print(f"Method 3 (CurrentFontWindow.selectedGlyphNames) found: {selected_names}")
                except Exception as e:
                    print(f"Method 3 failed: {e}")
            
            # Method 4: Fallback to current glyph
            if not selected_names:
                try:
                    current_glyph = CurrentGlyph()
                    if current_glyph:
                        selected_names = [current_glyph.name]
                        print(f"Method 4 (CurrentGlyph) found: {selected_names}")
                except Exception as e:
                    print(f"Method 4 failed: {e}")
            
            # Validate and set selection
            if selected_names:
                valid_names = []
                for name in selected_names:
                    if name in self.font:
                        valid_names.append(name)
                
                if valid_names:
                    self.selected_glyphs = valid_names
                    self.update_count()
                    self.w.action_group.status_label.set(f"Got {len(valid_names)} selected glyphs")
                else:
                    self.w.action_group.status_label.set("Selected glyphs not found in font")
            else:
                self.w.action_group.status_label.set("No glyphs selected in RoboFont")
                
        except Exception as e:
            print(f"Error in get_selected: {e}")
            self.w.action_group.status_label.set("Error getting selection")
    

    
    def select_all(self, sender):
        if self.font:
            self.selected_glyphs = [g.name for g in self.font]
            self.update_count()
            self.w.action_group.status_label.set(f"Selected all {len(self.selected_glyphs)} glyphs")
    
    def update_count(self):
        count = len(self.selected_glyphs)
        self.w.glyph_group.count_label.set(f"({count}) selected glyphs")
    
    def update_layers(self, sender):
        if not self.font:
            return
            
        layers = ["foreground"]
        if hasattr(self.font, 'layers'):
            try:
                # Handle different layer object types
                if hasattr(self.font.layers, 'keys'):
                    layer_names = self.font.layers.keys()
                elif hasattr(self.font.layers, '__iter__'):
                    layer_names = list(self.font.layers)
                else:
                    layer_names = []
                
                for layer_name in layer_names:
                    # Convert to string if it's a layer object
                    if hasattr(layer_name, 'name'):
                        layer_name = layer_name.name
                    elif not isinstance(layer_name, str):
                        layer_name = str(layer_name)
                    
                    if layer_name != "foreground":
                        layers.append(layer_name)
            except Exception as e:
                print(f"Error getting layers: {e}")
        
        self.w.layer_group.source_popup.setItems(layers)
        if layers:
            self.w.layer_group.source_popup.set(0)
    
    def copy_glyph_metrics(self, source_glyph, target_glyph, glyph_name: str) -> bool:
        """
        Copy metrics (width, leftMargin, rightMargin) from source to target glyph.
        
        Args:
            source_glyph: Source glyph object
            target_glyph: Target glyph object
            glyph_name: Name of the glyph for logging
            
        Returns:
            True if successful, False if failed
        """
        try:
            # Get source metrics
            source_width = getattr(source_glyph, 'width', 0)
            source_left_margin = getattr(source_glyph, 'leftMargin', 0)
            source_right_margin = getattr(source_glyph, 'rightMargin', 0)
            
            # Store original target metrics for logging
            original_width = getattr(target_glyph, 'width', 0)
            original_left = getattr(target_glyph, 'leftMargin', 0)
            original_right = getattr(target_glyph, 'rightMargin', 0)
            
            # Apply source metrics to target
            target_glyph.width = source_width
            target_glyph.leftMargin = source_left_margin
            target_glyph.rightMargin = source_right_margin
            
            print(f"Copied metrics for '{glyph_name}': W{original_width}→{source_width}, L{original_left}→{source_left_margin}, R{original_right}→{source_right_margin}")
            return True
            
        except Exception as e:
            print(f"Error copying metrics for {glyph_name}: {e}")
            return False
    
    def duplicate(self, sender):
        try:
            if not self.selected_glyphs:
                self.w.action_group.status_label.set("No glyphs selected")
                return
                
            if not self.font:
                self.w.action_group.status_label.set("No font open")
                return
            
            print(f"Starting duplication for {len(self.selected_glyphs)} glyphs: {self.selected_glyphs}")
            
            # Get parameters
            source_layer = self.w.layer_group.source_popup.getItems()[self.w.layer_group.source_popup.get()]
            target_layer = self.w.layer_group.target_field.get().strip()
            duplicate_metrics = self.w.metrics_group.duplicate_metrics.get()
            
            print(f"Source layer: {source_layer}")
            print(f"Target layer: {target_layer}")
            print(f"Duplicate metrics: {duplicate_metrics}")
            
            if not target_layer:
                self.w.action_group.status_label.set("Enter target layer name")
                return
            
            # Get transformations
            flip_h = self.w.transform_group.flip_h.get()
            flip_v = self.w.transform_group.flip_v.get()
            try:
                rotate = float(self.w.transform_group.rotate_field.get() or 0)
                scale = float(self.w.transform_group.scale_field.get() or 100) / 100.0
            except:
                self.w.action_group.status_label.set("Invalid transform values")
                return
            
            print(f"Transformations: flip_h={flip_h}, flip_v={flip_v}, rotate={rotate}, scale={scale}")
            
            # Create target layer if needed
            if target_layer not in self.font.layers:
                print(f"Creating new layer: {target_layer}")
                self.font.newLayer(target_layer)
            
            # Process each glyph
            processed = 0
            metrics_copied = 0
            for glyph_name in self.selected_glyphs:
                print(f"Processing glyph: {glyph_name}")
                if glyph_name in self.font:
                    glyph = self.font[glyph_name]
                    
                    # Get source and target
                    try:
                        if source_layer == "foreground":
                            source = glyph
                        else:
                            source = glyph.getLayer(source_layer)
                        
                        if target_layer == "foreground":
                            target = glyph
                        else:
                            target = glyph.getLayer(target_layer)
                        
                        print(f"Source: {source}, Target: {target}")
                        print(f"Source exists: {source is not None}, Target exists: {target is not None}")
                        print(f"Source type: {type(source)}, Target type: {type(target)}")
                        
                        # Check if we can access the layers
                        try:
                            source_test = source.contours
                            target_test = target.contours
                            print(f"Source contours: {len(source_test)}, Target contours: {len(target_test)}")
                            
                            # Clear target
                            target.clear()
                            
                            # Copy contours
                            for contour in source.contours:
                                new_contour = target.appendContour(contour)
                            
                            # Copy components
                            for component in source.components:
                                target.appendComponent(component.baseGlyph, component.transformation)
                            
                            # Copy anchors
                            for anchor in source.anchors:
                                target.appendAnchor(anchor.name, (anchor.x, anchor.y))
                            
                            # Apply transformations
                            if scale != 1.0:
                                target.scale(scale)
                            if rotate != 0:
                                target.rotate(math.radians(rotate))
                            if flip_h:
                                target.scale((-1, 1))
                            if flip_v:
                                target.scale((1, -1))
                            
                            # Copy metrics if requested
                            if duplicate_metrics:
                                if self.copy_glyph_metrics(source, target, glyph_name):
                                    metrics_copied += 1
                            
                            target.changed()
                            processed += 1
                            print(f"Successfully processed {glyph_name}")
                            
                        except Exception as e:
                            print(f"Error accessing layers for {glyph_name}: {e}")
                            continue
                    except Exception as e:
                        print(f"Error processing {glyph_name}: {e}")
                else:
                    print(f"Glyph {glyph_name} not found in font")
            
            self.font.changed()
            
            # Update status message
            status_msg = f"Duplicated {processed} glyphs to '{target_layer}'"
            if duplicate_metrics and metrics_copied > 0:
                status_msg += f" (metrics copied: {metrics_copied})"
            
            self.w.action_group.status_label.set(status_msg)
            print(f"Duplication complete: {processed} glyphs processed, {metrics_copied} metrics copied")
            
        except Exception as e:
            print(f"Error in duplicate: {e}")
            self.w.action_group.status_label.set(f"Error: {e}")

def main():
    if not CurrentFont():
        print("Please open a font first.")
        return
    MRLDuplicateLayers()

if __name__ == "__main__":
    main() 