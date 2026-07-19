# MRL Space Twin - Controller (Simplified)
# Developed by Kevin Kuhn (Mining Raw Letters)

from mojo.UI import AllSpaceCenters, GetFile
from vanilla import Window, List, Button, TextBox

class MRL_SpaceTwinController:
    """
    Simplified controller for MRL Space Twin extension - basic UFO pairing only.
    """

    def __init__(self):
        """
        Initializes the simplified Space Twin controller and UI.
        """
        print("MRL Space Twin: Initializing simplified version...")
        
        self.paired_centers = []  # List of paired Space Center tuples (master, twin)
        self.selected_master = None  # Currently selected master Space Center
        self.selected_twin = None  # Currently selected twin Space Center
        
        try:
            self.create_ui()
            print("MRL Space Twin: Successfully initialized!")
        except Exception as e:
            print(f"MRL Space Twin: Error during initialization: {e}")
            import traceback
            traceback.print_exc()

    def create_ui(self):
        """
        Creates the simplified management UI.
        """
        self.w = Window((320, 400), "MRL Space Twin", minSize=(300, 380))
        
        margin = 10
        y = margin
        
        # Available Space Centers
        self.w.spaceCentersText = TextBox((margin, y, -margin, 18), "Available Space Centers:", sizeStyle="small")
        y += 20
        
        column_descriptions = [{"title": "Font Name"}, {"title": "Status"}]
        self.w.spaceCentersList = List((margin, y, -margin, 100), [], 
                                      columnDescriptions=column_descriptions,
                                      selectionCallback=self.space_center_selected_callback)
        y += 110
        
        # Master and Twin selection buttons
        self.w.setMasterButton = Button((margin, y, 95, 25), "Set Master", 
                                       callback=self.set_master_callback)
        self.w.setTwinButton = Button((margin + 105, y, 95, 25), "Set Twin", 
                                     callback=self.set_twin_callback)
        y += 35
        
        # Status display
        self.w.masterStatus = TextBox((margin, y, -margin, 18), "Master: None", sizeStyle="small")
        y += 20
        self.w.twinStatus = TextBox((margin, y, -margin, 18), "Twin: None", sizeStyle="small")
        y += 30
        
        # Pairing button with smiley
        self.w.pairButton = Button((margin, y, -margin, 35), "Pair :-)", 
                                  callback=self.pair_callback, sizeStyle="regular")
        y += 45
        
        # Active pairs section
        self.w.pairsText = TextBox((margin, y, -margin, 18), "Active Pairs:", sizeStyle="small")
        y += 20
        
        column_descriptions = [{"title": "Master"}, {"title": "Twin"}]
        self.w.pairsList = List((margin, y, -margin, -60), [], 
                               columnDescriptions=column_descriptions,
                               selectionCallback=self.pair_selected_callback)
        
        # Bottom buttons
        self.w.unpairButton = Button((margin, -margin - 30, 80, 25), "Unpair", 
                                    callback=self.unpair_callback)
        self.w.closeButton = Button((-margin - 60, -margin - 30, 60, 25), "Close", 
                                   callback=self.close_callback)
        
        # Add window focus callback
        self.w.bind("became key", self.window_focus_callback)
        
        self.w.open()
        
        # Initial UI update after window opens
        self.update_ui()

    def window_focus_callback(self, sender):
        """
        Updates UI when window gains focus.
        """
        self.update_ui()

    def space_center_selected_callback(self, sender):
        """
        Handles Space Center selection in the list.
        """
        pass  # Simple selection, no additional logic needed

    def set_master_callback(self, sender):
        """
        Sets the selected Space Center as master.
        """
        selection = self.w.spaceCentersList.getSelection()
        if not selection:
            print("MRL Space Twin: No Space Center selected")
            return
        
        available_centers = self.get_available_centers()
        if not available_centers or selection[0] >= len(available_centers):
            print("MRL Space Twin: Invalid selection")
            return
        
        self.selected_master = available_centers[selection[0]]
        master_name = self.get_space_center_name(self.selected_master)
        print(f"MRL Space Twin: Set master to {master_name}")
        
        # Update master status
        self.w.masterStatus.set(f"Master: {master_name}")
        self.update_ui()

    def set_twin_callback(self, sender):
        """
        Sets the selected Space Center as twin.
        """
        selection = self.w.spaceCentersList.getSelection()
        if not selection:
            print("MRL Space Twin: No Space Center selected")
            return
        
        available_centers = self.get_available_centers()
        if not available_centers or selection[0] >= len(available_centers):
            print("MRL Space Twin: Invalid selection")
            return
        
        selected_center = available_centers[selection[0]]
        
        # Don't allow same center as master
        if selected_center == self.selected_master:
            print("MRL Space Twin: Cannot set same Space Center as both master and twin")
            return
        
        self.selected_twin = selected_center
        twin_name = self.get_space_center_name(self.selected_twin)
        print(f"MRL Space Twin: Set twin to {twin_name}")
        
        # Update twin status
        self.w.twinStatus.set(f"Twin: {twin_name}")
        self.update_ui()

    def pair_callback(self, sender):
        """
        Handles the Pair :-) button click.
        """
        if not self.selected_master:
            print("MRL Space Twin: No master selected. Please select a master first.")
            return
        
        if not self.selected_twin:
            print("MRL Space Twin: No twin selected. Please select a twin first.")
            return
        
        # Create the pair
        self.create_pair(self.selected_master, self.selected_twin)
        
        # Clear selections after pairing
        self.selected_master = None
        self.selected_twin = None
        self.w.masterStatus.set("Master: None")
        self.w.twinStatus.set("Twin: None")
        
        # Update UI
        self.update_ui()

    def create_pair(self, master_center, twin_center):
        """
        Creates a pairing between master and twin centers.
        """
        master_name = self.get_space_center_name(master_center)
        twin_name = self.get_space_center_name(twin_center)
        
        # Check if already paired
        for pair in self.paired_centers:
            if pair[0] == master_center and pair[1] == twin_center:
                print(f"MRL Space Twin: Already paired {master_name} with {twin_name}")
                return
        
        # Add to paired centers
        self.paired_centers.append((master_center, twin_center))
        print(f"MRL Space Twin: Paired {master_name} with {twin_name}")
        
        # Simple one-time sync of current text
        try:
            current_text = master_center.getRaw()
            twin_center.setRaw(current_text)
            print(f"MRL Space Twin: Synced text: '{current_text}'")
        except Exception as e:
            print(f"MRL Space Twin: Error syncing text: {e}")

    def get_available_centers(self):
        """
        Gets list of available Space Centers.
        """
        try:
            all_centers = AllSpaceCenters()
            return [center for center in all_centers if center is not None]
        except Exception as e:
            print(f"MRL Space Twin: Error getting Space Centers: {e}")
            return []

    def get_space_center_name(self, space_center):
        """
        Gets a display name for a Space Center.
        """
        try:
            if hasattr(space_center, 'font') and space_center.font:
                font = space_center.font
                if hasattr(font, 'path') and font.path:
                    import os
                    return os.path.basename(font.path)
                elif hasattr(font, 'info') and font.info and hasattr(font.info, 'familyName'):
                    family_name = font.info.familyName or "Untitled"
                    style_name = getattr(font.info, 'styleName', '') or "Regular"
                    return f"{family_name} {style_name}"
            return "Unknown Font"
        except Exception as e:
            print(f"MRL Space Twin: Error getting space center name: {e}")
            return "Unknown Font"

    def is_center_paired(self, center):
        """
        Checks if a Space Center is already part of a pair.
        """
        for master, twin in self.paired_centers:
            if center == master or center == twin:
                return True
        return False

    def update_ui(self):
        """
        Updates the UI with current state.
        """
        try:
            # Get available Space Centers
            available_centers = self.get_available_centers()
            
            # Update Space Centers list
            space_center_items = []
            for center in available_centers:
                name = self.get_space_center_name(center)
                
                # Determine status
                if center == self.selected_master:
                    status = "MASTER"
                elif center == self.selected_twin:
                    status = "TWIN"
                elif self.is_center_paired(center):
                    status = "Paired"
                else:
                    status = "Available"
                
                space_center_items.append({"Font Name": name, "Status": status})
            
            self.w.spaceCentersList.set(space_center_items)
            
            # Update pairs list
            pairs_data = []
            for master, twin in self.paired_centers:
                master_name = self.get_space_center_name(master)
                twin_name = self.get_space_center_name(twin)
                pairs_data.append({"Master": master_name, "Twin": twin_name})
            
            self.w.pairsList.set(pairs_data)
            
        except Exception as e:
            print(f"MRL Space Twin: Error updating UI: {e}")

    def pair_selected_callback(self, sender):
        """
        Handles selection of a pair in the pairs list.
        """
        pass  # Selection handled, unpair button will use this

    def unpair_callback(self, sender):
        """
        Removes the selected pair.
        """
        selection = self.w.pairsList.getSelection()
        if not selection or not self.paired_centers:
            print("MRL Space Twin: No pair selected")
            return
        
        index = selection[0]
        if index < len(self.paired_centers):
            master, twin = self.paired_centers[index]
            master_name = self.get_space_center_name(master)
            twin_name = self.get_space_center_name(twin)
            print(f"MRL Space Twin: Unpaired {master_name} <-> {twin_name}")
            self.paired_centers.pop(index)
            self.update_ui()

    def close_callback(self, sender):
        """
        Closes the extension window.
        """
        self.w.close()

    def __del__(self):
        """
        Cleanup when controller is destroyed.
        """
        try:
            if hasattr(self, 'w') and self.w:
                self.w.close()
        except:
            pass 