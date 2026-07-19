# MRL_Batch_Test_Install Main Script
# Developed by Kevin Kuhn (Mining Raw Letters)

import AppKit
from mojo.tools import CallbackWrapper
from mojo.roboFont import OpenWindow

import mrl_batch_test_install


class MrlBatchTestInstallMenu(object):
    """
    Menu integration for MRL Batch Test Install extension.
    Adds menu item to File menu for easy access.
    """
    
    def __init__(self):
        self._add_menu_item()
    
    def _add_menu_item(self):
        """Add batch test install menu item to File menu."""
        title = "MRL Batch Test Install..."
        main_menu = AppKit.NSApp().mainMenu()
        file_menu = main_menu.itemWithTitle_("File")
        
        if not file_menu:
            return
        
        file_menu = file_menu.submenu()
        
        # Check if menu item already exists
        if file_menu.itemWithTitle_(title):
            return
        
        # Find position after "Test Install All"
        test_install_index = file_menu.indexOfItemWithTitle_("Test Install All")
        if test_install_index == -1:
            # Fallback: add after "Test Install"
            test_install_index = file_menu.indexOfItemWithTitle_("Test Install")
        
        if test_install_index == -1:
            # Final fallback: add at end
            test_install_index = file_menu.numberOfItems()
        
        # Create menu item
        self.target = CallbackWrapper(self._menu_callback)
        new_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            title, "action:", ""
        )
        new_item.setTarget_(self.target)
        
        # Insert menu item
        file_menu.insertItem_atIndex_(new_item, test_install_index + 1)
    
    def _menu_callback(self, sender):
        """Handle menu item selection."""
        OpenWindow(mrl_batch_test_install.MrlBatchTestInstallController)


# Initialize the menu
MrlBatchTestInstallMenu() 