# MRL String Library - Controller
# Developed by Kevin Kuhn (Mining Raw Letters)

import os
from mojo.UI import CurrentSpaceCenter, getDefault, setDefault, GetFile, Message
from vanilla import Window, List, PopUpButton, EditText, Button

EXTENSION_KEY = "com.miningrawletters.stringLibrary.path"

class MRL_StringLibraryController:
    """
    Controller for the MRL String Library extension window.
    """

    def __init__(self):
        """
        Initializes the window and its UI components.
        """
        self.w = Window((300, 400), "MRL String Library", minSize=(250, 300))

        # Layout with explicit coordinates
        margin = 10
        y = margin
        
        # Category popup
        self.w.categoryPopUp = PopUpButton((margin, y, -margin, 20), [], callback=self.category_selected_callback)
        y += 30
        
        # String list with single-click support
        column_descriptions = [{"title": "String"}]
        self.w.stringList = List((margin, y, -margin, -70), [], 
                                columnDescriptions=column_descriptions, 
                                selectionCallback=self.string_selected_callback)
        
        # Bottom section with input and buttons
        bottom_y = -60
        button_height = 22
        
        # Add string input and button
        self.w.addStringInput = EditText((margin, bottom_y, -(margin + 60), button_height), placeholder="Add new string...")
        self.w.addButton = Button((-margin - 50, bottom_y, 50, button_height), "Add", callback=self.add_string_callback)
        
        # Delete, capture and settings buttons
        bottom_y += 30
        self.w.deleteButton = Button((margin, bottom_y, 80, button_height), "Delete", callback=self.delete_string_callback)
        self.w.captureButton = Button((margin + 90, bottom_y, 80, button_height), "Capture", callback=self.capture_string_callback)
        self.w.settingsButton = Button((-margin - 30, bottom_y, 30, button_height), "⚙", callback=self.settings_callback)
        


        self.load_data()
        self.w.open()

    def load_data(self):
        """
        Loads the markdown file path from preferences and populates the UI.
        """
        self.md_path = getDefault(EXTENSION_KEY)
        if not self.md_path or not os.path.exists(self.md_path):
            self.w.stringList.set([])
            self.w.categoryPopUp.setItems([])
            return

        self.string_data = self._parse_markdown(self.md_path)
        categories = sorted(self.string_data.keys())
        
        self.w.categoryPopUp.setItems(categories)
        self.update_string_list()

    def _parse_markdown(self, file_path):
        """
        Parses the markdown file and returns a dictionary of strings by category.
        """
        data = {}
        current_category = None
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    current_category = line.lstrip('# ').strip()
                    if current_category not in data:
                        data[current_category] = []
                elif line.startswith('- '):
                    string_item = line.lstrip('- ').strip()
                    if current_category is None:
                        # Handle strings that appear before any category heading
                        if "Uncategorized" not in data:
                            data["Uncategorized"] = []
                        data["Uncategorized"].append(string_item)
                    else:
                        data[current_category].append(string_item)
        return data

    def _save_markdown(self):
        """
        Saves the current string_data back to the markdown file.
        """
        if not self.md_path:
            return
            
        with open(self.md_path, 'w', encoding='utf-8') as f:
            for category, strings in self.string_data.items():
                f.write(f"# {category}\n\n")
                for string in strings:
                    f.write(f"- {string}\n")
                f.write("\n")

    def update_string_list(self):
        """
        Updates the string list based on the selected category.
        """
        selected_category_index = self.w.categoryPopUp.get()
        if selected_category_index is None or not self.w.categoryPopUp.getItems():
            self.w.stringList.set([])
            return
            
        categories = self.w.categoryPopUp.getItems()
        selected_category = categories[selected_category_index]
        
        list_items = [{"String": s} for s in self.string_data.get(selected_category, [])]
        self.w.stringList.set(list_items)
        
    def category_selected_callback(self, sender):
        """
        Called when the user selects a new category.
        """
        self.update_string_list()

    def string_selected_callback(self, sender):
        """
        Called when the user selects a string; automatically sends it to Space Center.
        """
        self._send_selected_string()

    def _send_selected_string(self):
        """
        Sends the selected string to the Space Center.
        """
        try:
            space_center = CurrentSpaceCenter()
            if not space_center:
                return
            
            selection = self.w.stringList.getSelection()
            if not selection:
                return

            selected_item = self.w.stringList[selection[0]]
            space_center.setRaw(selected_item["String"])
        except Exception as e:
            pass

    def add_string_callback(self, sender):
        """
        Adds a new string to the selected category and saves to markdown file.
        """
        new_string = self.w.addStringInput.get().strip()
        if not new_string:
            return

        if not self.md_path or not os.path.exists(self.md_path):
             return

        selected_category_index = self.w.categoryPopUp.get()
        if selected_category_index is None or not self.w.categoryPopUp.getItems():
             return
        
        categories = self.w.categoryPopUp.getItems()
        selected_category = categories[selected_category_index]

        # Add to data structure
        self.string_data.setdefault(selected_category, []).append(new_string)
        
        # Save entire file
        self._save_markdown()
        
        # Clear input and refresh list
        self.w.addStringInput.set("")
        self.update_string_list()

    def capture_string_callback(self, sender):
        """
        Captures the current text from Space Center and adds it to the selected category.
        """
        try:
            space_center = CurrentSpaceCenter()
            if not space_center:
                return
            
            # Get the current text from Space Center
            current_text = space_center.getRaw()
            if not current_text or not current_text.strip():
                return
            
            current_text = current_text.strip()
            
            if not self.md_path or not os.path.exists(self.md_path):
                return

            selected_category_index = self.w.categoryPopUp.get()
            if selected_category_index is None or not self.w.categoryPopUp.getItems():
                return
            
            categories = self.w.categoryPopUp.getItems()
            selected_category = categories[selected_category_index]

            # Check if string already exists in the category
            if current_text in self.string_data.get(selected_category, []):
                return
            
            # Add to data structure
            self.string_data.setdefault(selected_category, []).append(current_text)
            
            # Save entire file
            self._save_markdown()
            
            # Refresh list
            self.update_string_list()
            
        except Exception as e:
            pass

    def delete_string_callback(self, sender):
        """
        Deletes the selected string from the category and markdown file.
        """
        selection = self.w.stringList.getSelection()
        if not selection:
            return

        selected_category_index = self.w.categoryPopUp.get()
        if selected_category_index is None:
            return
            
        categories = self.w.categoryPopUp.getItems()
        selected_category = categories[selected_category_index]
        
        # Get the string to delete
        selected_item = self.w.stringList[selection[0]]
        string_to_delete = selected_item["String"]
        
        # Remove from data structure
        if selected_category in self.string_data and string_to_delete in self.string_data[selected_category]:
            self.string_data[selected_category].remove(string_to_delete)
            
            # Save entire file
            self._save_markdown()
            
            # Refresh list
            self.update_string_list()
        
    def settings_callback(self, sender):
        """
        Opens a file dialog to choose a new markdown file.
        """
        new_path = GetFile("Select your strings markdown file", fileTypes=["md", "txt"])
        if new_path:
            setDefault(EXTENSION_KEY, new_path)
            self.load_data()

if __name__ == '__main__':
    MRL_StringLibraryController() 