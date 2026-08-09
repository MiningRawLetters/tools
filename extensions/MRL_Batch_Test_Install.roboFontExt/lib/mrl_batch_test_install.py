# MRL_Batch_Test_Install Controller
# Developed by Kevin Kuhn (Mining Raw Letters)

import os
import time
import AppKit
import ezui
from typing import List, Dict, Optional, Any

from mojo.roboFont import OpenFont, AllFonts, CurrentFont
from mojo.extensions import getExtensionDefault, setExtensionDefault
from lib.tools.misc import walkDirectoryForFile


def _build_font_table_items(font_paths: List[str]) -> List[Dict[str, Any]]:
    """Build table items from font paths."""
    return [{"source": path} for path in font_paths]


def _get_open_font_paths() -> List[str]:
    """Get paths of all open fonts that are saved."""
    return [font.path for font in AllFonts() if font.path is not None]


def _validate_font_path(path: str) -> bool:
    """Validate if path is a supported font format."""
    supported_extensions = ['.ufo', '.designspace', '.otf', '.ttf']
    return any(path.lower().endswith(ext) for ext in supported_extensions)


def _test_install_single_font(font_path: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Test install a single font and return result."""
    try:
        # Check if font is already open in RoboFont
        already_open_font = None
        for open_font in AllFonts():
            if open_font.path == font_path:
                already_open_font = open_font
                break
        
        # Use existing font if already open, otherwise open from disk
        if already_open_font:
            font = already_open_font
            should_close = False
        else:
            font = OpenFont(font_path, showInterface=False)
            should_close = True
        
        # Store original PostScript name for restoration
        original_name = font.info.postscriptFontName
        
        # Apply settings if needed
        if settings.get('unique_postscript_name', False):
            if original_name:
                font.info.postscriptFontName = f"{original_name}-{int(time.time())}"
        
        # Test install
        font.testInstall()
        
        result = {
            'path': font_path,
            'font_name': font.info.familyName or 'Unknown',
            'postscript_name': font.info.postscriptFontName or 'Unknown'
        }
        
        # Restore original PostScript name if it was changed
        if settings.get('unique_postscript_name', False) and original_name:
            font.info.postscriptFontName = original_name
        
        # Only close if we opened it (not if it was already open)
        if should_close:
            font.close()
        
        return result
        
    except Exception as error:
        return {
            'path': font_path,
            'error': str(error)
        }


def _add_paths_to_table(table: Any, paths: List[str]) -> None:
    """Add new paths to table if they don't already exist."""
    if not paths:
        return
    
    existing_sources = [item["source"] for item in table.getArrangedItems()]
    new_items = []
    
    for path in paths:
        if path not in existing_sources and _validate_font_path(path):
            new_items.append(table.makeItem(source=path))
    
    if new_items:
        table.appendItems(new_items)


class MrlBatchTestInstallController(ezui.WindowController):
    """
    Main controller for MRL Batch Test Install extension.
    Provides interface for batch test installing multiple fonts.
    """
    
    supported_file_types = ["ufo", "designspace", "otf", "ttf"]
    
    def build(self, sources: List[str] = None) -> None:
        """Build the main window interface."""
        sources = sources or []
        
        content = """
        #= ScrollingVerticalStack
        * Table                                            @sources
        * TextField                                        @selectedPath
        * HorizontalStack
        > (+-)                                             @sourcesAddRemoveButton
        > ( Add Open UFO )                                 @sourcesAddOpenFontsButton
        
        * HorizontalStack
        > ( Clear All )                                    @clearAll
        > ( Test Install All )                             @testInstallAll
        """
        
        description_data = {
            "sources": {
                "columnDescriptions": [
                    {"identifier": "source", "title": "File Name", "width": 900}
                ],
                "showColumnTitles": True,
                "enableDelete": True,
                "selectionCallback": self._sources_selection_callback,
                "items": _build_font_table_items(sources),
                "dropSettings": {
                    "pasteboardTypes": ["fileURL"],
                    "dropCandidateCallback": self._sources_drop_candidate_callback,
                    "performDropCallback": self._sources_perform_drop_callback
                }
            },
            "sourcesAddOpenFontsButton": {
                "gravity": "trailing",
            },
            "selectedPath": {
                "value": "",
                "placeholder": "Selected path…",
                "sizeStyle": "small"
            },
            "clearAll": {
                "width": 100
            },
            "testInstallAll": {
                "width": 120
            }
        }
        
        self.w = ezui.EZWindow(
            title="MRL Batch Test Install",
            content=content,
            descriptionData=description_data,
            size=(475, 250),
            minSize=(400, 220),
            maxSize=(1800, 500),
            defaultButton="testInstallAll",
            controller=self,
        )
    
    def _sources_selection_callback(self, sender: Any) -> None:
        """Update the selectedPath field with the full path of the selected row."""
        try:
            items = sender.getSelectedItems()
        except Exception:
            # Fallback if API differs
            items = []
        path = items[0]["source"] if items else ""
        self.w.setItemValues({"selectedPath": path})
    
    def started(self) -> None:
        """Called when window is opened."""
        # Load saved settings
        saved_settings = getExtensionDefault("com.mrl.batchTestInstall", {})
        
        # Filter out non-interface settings
        ui_settings = {k: v for k, v in saved_settings.items() 
                      if k in self.w.getItemValues().keys()}
        
        if ui_settings:
            self.w.setItemValues(ui_settings)
        
        self.w.open()
    
    def destroy(self) -> None:
        """Called when window is closed."""
        # Save settings
        settings = self.w.getItemValues()
        # Remove non-persistent items
        for key in ("sources",):
            settings.pop(key, None)
        
        setExtensionDefault("com.mrl.batchTestInstall", settings)
    
    # Button Callbacks
    
    def sourcesAddRemoveButtonAddCallback(self, sender: Any) -> None:
        """Handle add button click."""
        def result(paths: List[str]) -> None:
            _add_paths_to_table(self.w.getItem("sources"), paths)
        
        self.showGetFile(
            callback=result,
            fileTypes=self.supported_file_types,
            allowsMultipleSelection=True
        )
    
    def sourcesAddRemoveButtonRemoveCallback(self, sender: Any) -> None:
        """Handle remove button click."""
        table = self.w.getItem("sources")
        table.removeSelectedItems()
    
    def sourcesAddOpenFontsButtonCallback(self, sender: Any) -> None:
        """Add all open UFO to the list."""
        paths = _get_open_font_paths()
        _add_paths_to_table(self.w.getItem("sources"), paths)
    
    def clearAllCallback(self, sender: Any) -> None:
        """Clear all UFO from the list."""
        table = self.w.getItem("sources")
        items = table.getArrangedItems()
        
        if items:
            # Clear all items by removing them one by one
            for i in range(len(items)):
                # Always remove the first item until table is empty
                remaining_items = table.getArrangedItems()
                if remaining_items:
                    table.removeItems([remaining_items[0]])
    
    def testInstallAllCallback(self, sender: Any) -> None:
        """Test install all UFO in the list."""
        table = self.w.getItem("sources")
        items = table.getArrangedItems()
        
        if not items:
            return
        
        # Simple settings - no unique postscript names, no progress details
        settings = {
            'unique_postscript_name': False,
            'show_progress_details': False
        }
        
        for item in items:
            font_path = item["source"]
            _test_install_single_font(font_path, settings)
    
    # Drop Callbacks
    
    def _sources_drop_candidate_callback(self, info: Dict[str, Any]) -> str:
        """Handle drop candidate validation."""
        table = self.w.getItem("sources")
        dropped_items = info["sender"].getDropItemValues(info["items"], "fileURL")
        existing_sources = [item["source"] for item in table.getArrangedItems()]
        
        valid_items = []
        for item in dropped_items:
            path = item.path()
            if path not in existing_sources and _validate_font_path(path):
                valid_items.append(path)
        
        return "link" if valid_items else "none"
    
    def _sources_perform_drop_callback(self, info: Dict[str, Any]) -> None:
        """Handle actual drop operation."""
        sender = info["sender"]
        items = sender.getDropItemValues(info["items"], "fileURL")
        paths = [item.path() for item in items]
        
        valid_paths = [path for path in paths if _validate_font_path(path)]
        _add_paths_to_table(self.w.getItem("sources"), valid_paths)


# Make the controller available for import
__all__ = ["MrlBatchTestInstallController"] 