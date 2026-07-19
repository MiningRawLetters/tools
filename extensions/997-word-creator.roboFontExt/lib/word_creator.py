# coding=utf-8
"""
997 Word Creator - A RoboFont extension that generates test words for type testing
Based on word-o-mat by Nina Stössinger, but implemented with functional programming principles

Developed by Kevin Kuhn
Version 1.0
"""

import codecs
import re
import os
import sys
import random
import webbrowser

# Make typing imports compatible with older Python versions
try:
    from typing import List, Dict, Tuple, Set, Optional, Any, Callable, Union
    HAS_TYPING = True
    
    # Define TypedDict for older Python versions
    try:
        from typing import TypedDict
    except ImportError:
        # Simple TypedDict replacement for older Python
        class TypedDict(dict):
            pass
except ImportError:
    HAS_TYPING = False
    # Create dummy type aliases for older Python versions
    List = Dict = Tuple = Set = Optional = Any = Callable = TypedDict = Union = type(None)

# Import UI components with fallbacks
try:
    from lib.UI.noneTypeColorWell import NoneTypeColorWell
except ImportError:
    # Simple fallback for color well
    class NoneTypeColorWell:
        def __init__(self, posSize, callback=None, color=None):
            self._color = color
            self._callback = callback
            
        def get(self):
            return self._color
            
        def set(self, color):
            self._color = color
            if self._callback:
                self._callback(self)

try:
    from lib.UI.spaceCenter.glyphSequenceEditText import GlyphSequenceEditText
except ImportError:
    pass

from mojo.events import addObserver, removeObserver
from mojo.extensions import getExtensionDefault, setExtensionDefault, ExtensionBundle
from mojo.roboFont import OpenWindow, CurrentFont, AllFonts
from mojo.UI import OpenSpaceCenter

# Check if AccordionView is available
has_accordion = False
try:
    from mojo.UI import AccordionView
    has_accordion = True
except ImportError:
    pass

# Import vanilla modules with fallbacks
from vanilla import *
try:
    from vanilla.dialogs import getFile, message, GetFile, Message
except ImportError:
    # Fallback implementations
    def getFile(**kwargs):
        print("File dialog not available")
        return None
        
    def message(messageText, informativeText="", alertStyle="info", buttonTitles=None, title=None, icon=None):
        """Fallback for vanilla message dialog"""
        print(f"DIALOG: {title or 'Message'} - {messageText}")
        print(f"INFO: {informativeText}")
        # Return 1 by default (usually corresponds to "OK" or primary action)
        return 1

try:
    from vanilla import dialogs
except ImportError:
    # Create a minimal fallback for vanilla dialogs
    class MinimalVanillaDialogs:
        def getDefault(self, message="", value=""):
            return value
    
    dialogs = MinimalVanillaDialogs()

# Type definitions for better code organization
class WordFilter(dict):
    """Dictionary type for word filter parameters"""
    pass

class WordSettings(dict):
    """Dictionary type for word settings parameters"""
    pass

# Constants
EXTENSION_KEY = "com.kevinkuhn.997wordcreator"
DEFAULT_PREFS = {
    "word_count": 20,
    "min_length": 3,
    "max_length": 15,
    "required_letters": "",
    "required_letters_only": False,
    "match_pattern": "",
    "ban_repetitions": False,
    "limit_to_charset": True,
    "custom_charset": "",
    "excluded_letters": "",
    "case_setting": "lowercase",
    "language": "english",
    "sort_by": "alphabetical",
    "sort_order": "ascending",
    "output_format": "space",  # space, newline, or comma
    "mark_glyphs": False,
    "mark_color": None,
    "save_to_file": False,
    "output_path": "",
    "sample_text": "",
    "load_preset": "",
    "save_preset": ""
}

# Available output formats
OUTPUT_FORMATS = [
    ("Space", "space"),
    ("New Line", "newline"),
    ("Comma", "comma"),
    ("Space Center", "spacecenter")
]

# Preset handling
def load_presets():
    """
    Load saved presets from extension defaults
    
    Returns:
        Dictionary of preset names to preset settings
    """
    presets = getExtensionDefault(f"{EXTENSION_KEY}.presets", {})
    if not presets:
        # Create some default presets if none exist
        presets = {
            "Default": DEFAULT_PREFS.copy(),
            "Ascenders": {
                **DEFAULT_PREFS,
                "match_pattern": "[bdfhklt]",
                "min_length": 4, 
                "max_length": 8
            },
            "Descenders": {
                **DEFAULT_PREFS,
                "match_pattern": "[gpqyj]",
                "min_length": 4,
                "max_length": 8
            },
            "No Rounds": {
                **DEFAULT_PREFS,
                "match_pattern": "^[^oOpPbBdDgGqQcC]*$"
            }
        }
        setExtensionDefault(f"{EXTENSION_KEY}.presets", presets)
    return presets

def save_preset(name, settings):
    """
    Save current settings as a preset
    
    Args:
        name: Name of the preset
        settings: Dictionary of settings to save
    """
    presets = load_presets()
    presets[name] = settings
    setExtensionDefault(f"{EXTENSION_KEY}.presets", presets)
    
def delete_preset(name):
    """
    Delete a preset
    
    Args:
        name: Name of the preset to delete
    """
    presets = load_presets()
    if name in presets:
        del presets[name]
        setExtensionDefault(f"{EXTENSION_KEY}.presets", presets)

# Import/export word lists
def import_wordlist(path=None):
    """
    Import a custom word list
    
    Args:
        path: Optional path to the wordlist file. If not provided, open a file dialog.
        
    Returns:
        Path to the imported word list
    """
    if not path:
        path = getFile(title="Select Word List", messageText="Choose a text file with one word per line.", 
                      fileTypes=["txt"])
    
    if not path:
        return None
        
    # Copy the file to the extension's resources
    try:
        bundle = ExtensionBundle("997 Word Creator")
        resources_path = bundle.resourcesPath()
        wordlist_dir = os.path.join(resources_path, "wordlists")
        
        if not os.path.exists(wordlist_dir):
            os.makedirs(wordlist_dir, exist_ok=True)
        
        filename = os.path.basename(path)
        language_name = os.path.splitext(filename)[0]
        
        # Check if it already exists
        if language_name == "english":
            dest_path = os.path.join(wordlist_dir, f"english_custom.txt")
            language_name = "english_custom"
        else:
            dest_path = os.path.join(wordlist_dir, filename)
        
        # Read and sanitize the custom wordlist
        with codecs.open(path, "r", encoding="utf-8", errors="ignore") as src_file:
            words = [line.strip() for line in src_file.readlines() if line.strip()]
        
        # Write the sanitized wordlist
        with codecs.open(dest_path, "w", encoding="utf-8") as dest_file:
            dest_file.write("\n".join(words))
        
        print(f"Imported word list: {language_name}")
        return dest_path
    except Exception as e:
        print(f"Error importing wordlist: {e}")
        return None

# Dictionary loading functions
def load_dictionaries():
    """
    Load dictionary file paths from the resources folder
    
    Returns:
        Dictionary mapping language names to file paths
    """
    dictionary_paths = {}
    try:
        bundle = ExtensionBundle("997 Word Creator")
        resources_path = bundle.resourcesPath()
        
        # Debug info - print paths to check what's happening
        print(f"Bundle path: {bundle.basePath()}")
        print(f"Resources path: {resources_path}")
        
        wordlist_dir = os.path.join(resources_path, "wordlists")
        print(f"Looking for wordlists in: {wordlist_dir}")
        
        if not os.path.exists(wordlist_dir):
            print(f"Wordlist directory not found: {wordlist_dir}")
            # Try alternate path
            fallback_path = os.path.join(resources_path, "en.txt")
            print(f"Trying fallback path: {fallback_path}")
            if os.path.exists(fallback_path):
                dictionary_paths["english"] = fallback_path
                print(f"Found fallback english.txt at: {fallback_path}")
            else:
                # Directly use a path relative to the extension root
                alt_path = os.path.join(bundle.basePath(), "resources", "wordlists", "english.txt")
                print(f"Trying alternative path: {alt_path}")
                if os.path.exists(alt_path):
                    dictionary_paths["english"] = alt_path
                    print(f"Found english.txt at: {alt_path}")
                else:
                    print(f"No dictionary files found!")
        else:
            # List all files in the directory for debugging
            print(f"Files in {wordlist_dir}:")
            for item in os.listdir(wordlist_dir):
                item_path = os.path.join(wordlist_dir, item)
                print(f"  - {item} ({'directory' if os.path.isdir(item_path) else 'file'}, {os.path.getsize(item_path)} bytes)")
            
            # Look for dictionary files
            for filename in os.listdir(wordlist_dir):
                if filename.endswith(".txt"):
                    language = os.path.splitext(filename)[0]
                    file_path = os.path.join(wordlist_dir, filename)
                    dictionary_paths[language] = file_path
                    print(f"Found dictionary for {language}: {file_path}")
        
        # If we still don't have a dictionary, create a basic one
        if not dictionary_paths and not os.path.exists(wordlist_dir):
            os.makedirs(wordlist_dir, exist_ok=True)
            english_path = os.path.join(wordlist_dir, "english.txt")
            with open(english_path, "w") as f:
                basic_words = ["apple", "banana", "cherry", "orange", "grape", "lemon", 
                              "peach", "plum", "melon", "fig", "date", "lime", "coconut", 
                              "mango", "pear", "apricot", "nectarine", "papaya", "kiwi", "avocado"]
                f.write("\n".join(basic_words))
            dictionary_paths["english"] = english_path
            print(f"Created basic English dictionary at: {english_path}")
    
    except Exception as e:
        print(f"Error in load_dictionaries: {e}")
        # Create a temporary dictionary in memory as a last resort
        print("Creating temporary dictionary in memory")
        temp_path = os.path.join(os.path.dirname(__file__), "temp_english.txt")
        with open(temp_path, "w") as f:
            f.write("temporary\nwords\nfallback\ntest\nfont")
        dictionary_paths["english"] = temp_path
    
    print(f"Final dictionary paths: {dictionary_paths}")
    return dictionary_paths

def read_word_list(path):
    """
    Read a wordlist file and return its contents as a list
    
    Args:
        path: Path to the wordlist file
        
    Returns:
        List of words from the file
    """
    try:
        with codecs.open(path, "r", encoding="utf-8") as file:
            words = [line.strip() for line in file if line.strip()]
        return words
    except (IOError, UnicodeDecodeError):
        return []

# Word filtering functions
def check_word(word, filter_params, font_chars=None):
    """
    Check if a word meets all the filter criteria
    
    Args:
        word: The word to check
        filter_params: Dictionary of filter parameters
        font_chars: Set of available characters in the font
        
    Returns:
        True if the word meets all criteria, False otherwise
    """
    # Check word length
    if len(word) < filter_params["min_length"] or len(word) > filter_params["max_length"]:
        return False
    
    # Check if word contains only font characters
    if filter_params["limit_to_charset"] and font_chars:
        if not all(char in font_chars for char in word):
            return False
    
    # Check if word contains custom charset characters
    if filter_params["custom_charset"]:
        custom_chars = set(filter_params["custom_charset"])
        if not all(char in custom_chars for char in word):
            return False
    
    # Check for excluded letters
    if filter_params.get("excluded_letters"):
        excluded = set(filter_params["excluded_letters"])
        if any(char in excluded for char in word):
            return False
    
    # Check for required letters
    if filter_params["required_letters"]:
        required = set(filter_params["required_letters"])
        if filter_params["required_letters_only"]:
            word_chars = set(word)
            if not required.issubset(word_chars):
                return False
        else:
            if not any(char in word for char in required):
                return False
    
    # Check for regular expression pattern
    if filter_params["match_pattern"]:
        try:
            pattern = re.compile(filter_params["match_pattern"])
            if not pattern.search(word):
                return False
        except re.error:
            # Invalid regex pattern, ignore this check
            pass
    
    # Check for banned repetitions
    if filter_params["ban_repetitions"]:
        for i in range(len(word)-1):
            if word[i] == word[i+1]:
                return False
    
    return True

def filter_words(words, filter_params, font_chars=None):
    """
    Filter a list of words based on the provided criteria
    
    Args:
        words: List of words to filter
        filter_params: Dictionary of filter parameters
        font_chars: Set of available characters in the font
        
    Returns:
        Filtered list of words
    """
    return [word for word in words if check_word(word, filter_params, font_chars)]

# Word processing functions
def apply_case(words, case_setting):
    """
    Apply case transformation to a list of words
    
    Args:
        words: List of words to transform
        case_setting: Case setting (lowercase, uppercase, titlecase, or random)
        
    Returns:
        List of words with the case transformation applied
    """
    if case_setting == "lowercase":
        return [word.lower() for word in words]
    elif case_setting == "uppercase":
        return [word.upper() for word in words]
    elif case_setting == "titlecase":
        return [word.title() for word in words]
    elif case_setting == "random":
        result = []
        for word in words:
            case_func = random.choice([str.lower, str.upper, str.title])
            result.append(case_func(word))
        return result
    else:
        return words

def sort_words(words, sort_by, sort_order, font=None):
    """
    Sort a list of words based on the specified criteria
    
    Args:
        words: List of words to sort
        sort_by: Sorting criterion (alphabetical, length, width)
        sort_order: Sort order (ascending or descending)
        font: Font object for width calculation (optional)
        
    Returns:
        Sorted list of words
    """
    reverse = sort_order == "descending"
    
    if sort_by == "alphabetical":
        return sorted(words, reverse=reverse)
    elif sort_by == "length":
        return sorted(words, key=len, reverse=reverse)
    elif sort_by == "width" and font:
        def get_word_width(word):
            try:
                width = 0
                for char in word:
                    glyph_name = font.unicodeData.glyphNameForUnicode(ord(char))
                    if glyph_name in font and font[glyph_name].width is not None:
                        width += font[glyph_name].width
                return width
            except:
                return 0
        return sorted(words, key=get_word_width, reverse=reverse)
    else:
        return words

def generate_words(
    word_count, 
    filter_params, 
    settings, 
    dictionary_path, 
    font=None
):
    """
    Generate a list of words based on the specified parameters
    
    Args:
        word_count: Number of words to generate
        filter_params: Dictionary of filter parameters
        settings: Dictionary of output settings
        dictionary_path: Path to the dictionary file
        font: Font object for filtering and sorting (optional)
        
    Returns:
        List of generated words
    """
    # Get font characters if limiting to charset
    font_chars = None
    if filter_params["limit_to_charset"] and font:
        font_chars = get_font_characters(font)
    
    # Debug dictionary path issues
    print(f"Using dictionary path: {dictionary_path}")
    print(f"Dictionary exists: {os.path.exists(dictionary_path)}")
    
    # Read and filter words
    all_words = read_word_list(dictionary_path)
    print(f"Found {len(all_words)} words in dictionary")
    
    filtered_words = filter_words(all_words, filter_params, font_chars)
    print(f"After filtering: {len(filtered_words)} words match criteria")
    
    # If not enough words meet the criteria, return what we have
    if len(filtered_words) < word_count:
        result = filtered_words
    else:
        # Randomly select words
        result = random.sample(filtered_words, word_count)
    
    # Apply case transformation
    result = apply_case(result, settings["case_setting"])
    
    # Sort words
    result = sort_words(result, settings["sort_by"], settings["sort_order"], font)
    
    return result

def format_output(words, output_format="space"):
    """
    Format a list of words based on the desired output format
    
    Args:
        words: List of words
        output_format: Output format (space, newline, comma)
        
    Returns:
        Formatted output string
    """
    if output_format == "space":
        return " ".join(words)
    elif output_format == "newline":
        return "\n".join(words)
    elif output_format == "comma":
        return ", ".join(words)
    else:
        return " ".join(words)

def save_output_to_file(words, output_path, output_format="space"):
    """
    Save the generated words to a file
    
    Args:
        words: List of words
        output_path: Path to save the file
        output_format: Output format (space, newline, comma)
        
    Returns:
        Boolean indicating success
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Format words
        formatted_output = format_output(words, output_format)
        
        # Write to file
        with codecs.open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        
        return True
    except Exception as e:
        print(f"Error saving output to file: {e}")
        return False

def mark_glyphs_in_font(words, font, color):
    """
    Mark glyphs that appear in the generated words in the font
    
    Args:
        words: List of words
        font: Font object
        color: Color to mark glyphs with
        
    Returns:
        Number of glyphs marked
    """
    if not font or not color:
        return 0
    
    marked_count = 0
    
    # Get unique characters from all words
    unique_chars = set("".join(words))
    
    # Mark each glyph
    for char in unique_chars:
        try:
            unicode_value = ord(char)
            glyph_name = font.unicodeData.glyphNameForUnicode(unicode_value)
            
            if glyph_name in font:
                glyph = font[glyph_name]
                glyph.markColor = color
                marked_count += 1
        except:
            pass
    
    return marked_count

# UI helper functions
def read_ext_default_boolean(key, default=False):
    """
    Read a boolean extension default, handling legacy string values
    
    Args:
        key: The settings key to read
        default: Default value if setting doesn't exist
        
    Returns:
        Boolean value of the setting
    """
    value = getExtensionDefault(f"{EXTENSION_KEY}.{key}", default)
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)

def write_ext_default_boolean(key, value):
    """
    Write a boolean extension default
    
    Args:
        key: The settings key to write
        value: The boolean value to store
    """
    setExtensionDefault(f"{EXTENSION_KEY}.{key}", bool(value))

def get_font_characters(font):
    """
    Get the set of characters available in a font
    
    Args:
        font: Font object
        
    Returns:
        Set of available characters
    """
    result = set()
    if not font:
        return result
    
    for glyph in font:
        if glyph.unicode:
            result.add(chr(glyph.unicode))
    
    return result

def validate_input(filter_params, font=None):
    """
    Validate the user input parameters
    
    Args:
        filter_params: Dictionary of filter parameters
        font: Font object (optional)
        
    Returns:
        Tuple containing a boolean (True if valid) and an error message (empty if valid)
    """
    # Check min vs max length
    if filter_params["min_length"] > filter_params["max_length"]:
        return (False, "Minimum length cannot be greater than maximum length")
    
    # Check required letters against font characters
    if filter_params["limit_to_charset"] and font and filter_params["required_letters"]:
        font_chars = get_font_characters(font)
        for char in filter_params["required_letters"]:
            if char not in font_chars:
                return (False, f"Required letter '{char}' not in font character set")
    
    # Check required letters vs max length
    if filter_params["required_letters_only"] and filter_params["required_letters"]:
        if len(set(filter_params["required_letters"])) > filter_params["max_length"]:
            return (False, "Too many required letters for maximum word length")
    
    # Check regex pattern
    if filter_params["match_pattern"]:
        try:
            re.compile(filter_params["match_pattern"])
        except re.error:
            return (False, "Invalid regular expression pattern")
    
    return (True, "")

# Additional fallback for showing messages
def ShowMessage(message_text, informative_text="", icon=None, title=None, button_titles=None):
    """
    Show a message dialog using whatever method is available.
    Falls back to print statements if no UI method is available.
    
    Args:
        message_text: The main message text
        informative_text: Additional information
        icon: Icon to display (ignored in fallback)
        title: Dialog title
        button_titles: List of button titles
        
    Returns:
        Index of button clicked (0-based) or 0 if not applicable
    """
    try:
        # Try using vanilla's message function
        from vanilla.dialogs import message as vanilla_message
        return vanilla_message(
            message_text, 
            informativeText=informative_text, 
            title=title or "Message", 
            buttonTitles=button_titles
        )
    except Exception:
        # Fall back to printing
        print(f"\n{'=' * 40}")
        print(f"MESSAGE: {title or 'Message'}")
        print(f"{message_text}")
        if informative_text:
            print(f"\n{informative_text}")
        print(f"{'=' * 40}\n")
        return 0  # Return 0 as default (usually "OK" button)

# The main UI window
class WordCreatorWindow(object):
    """
    The main window for the 997 Word Creator extension.
    
    Note: This is the only class in the extension, as it specifically handles UI interaction,
    which is better expressed in an object-oriented style. All actual functionality is 
    implemented in pure functions.
    """
    
    def __init__(self):
        # Load preferences
        self.prefs = self._load_preferences()
        self.dictionaries = load_dictionaries()
        self.presets = load_presets()
        
        # Set up window
        self.w = Window((320, 650), "997 Word Creator", minSize=(300, 550))
        
        # Panel 1: Basic Settings
        self.w.panel1 = Group((0, 0, -0, -0))
        y = 10
        
        # Presets UI
        self.w.panel1.presetsText = TextBox((10, y, 100, 22), "Preset:")
        self.w.panel1.presets = PopUpButton((110, y, -70, 22), list(self.presets.keys()), callback=self._load_preset_callback)
        self.w.panel1.savePresetButton = Button((-60, y, -10, 22), "Save", callback=self._save_preset_callback)
        
        y += 32
        self.w.panel1.sourceText = TextBox((10, y, 100, 22), "Source:")
        self.w.panel1.source = PopUpButton((110, y, -70, 22), list(self.dictionaries.keys()), callback=self._change_source_callback)
        self.w.panel1.importButton = Button((-60, y, -10, 22), "Import", callback=self._import_wordlist_callback)
        
        y += 32
        self.w.panel1.countText = TextBox((10, y, 100, 22), "Number of words:")
        self.w.panel1.countEdit = EditText((110, y, -10, 22), self.prefs["word_count"])
        
        y += 32
        self.w.panel1.minLengthText = TextBox((10, y, 100, 22), "Min length:")
        self.w.panel1.minLengthEdit = EditText((110, y, 50, 22), self.prefs["min_length"])
        self.w.panel1.maxLengthText = TextBox((170, y, 80, 22), "Max length:")
        self.w.panel1.maxLengthEdit = EditText((250, y, -10, 22), self.prefs["max_length"])
        
        y += 32
        self.w.panel1.limitToCharsetText = TextBox((10, y, -10, 22), "Limit to charset in current font")
        self.w.panel1.limitToCharset = CheckBox((10, y+22, -10, 22), "", value=self.prefs["limit_to_charset"], callback=self._toggle_limit_charset)
        
        # Panel 2: Letter Filters
        self.w.panel2 = Group((0, 0, -0, -0))
        y = 10
        self.w.panel2.requiredLettersText = TextBox((10, y, -10, 22), "Required letters:")
        self.w.panel2.requiredLettersEdit = EditText((10, y+22, -10, 22), self.prefs["required_letters"])
        
        y += 54
        self.w.panel2.requiredLettersOnlyText = TextBox((10, y, -10, 22), "All letters must be present in each word")
        self.w.panel2.requiredLettersOnly = CheckBox((10, y+22, -10, 22), "", value=self.prefs["required_letters_only"])
        
        y += 54
        self.w.panel2.excludedLettersText = TextBox((10, y, -10, 22), "Excluded letters:")
        self.w.panel2.excludedLettersEdit = EditText((10, y+22, -10, 22), self.prefs.get("excluded_letters", ""))
        
        y += 54
        self.w.panel2.banRepetitionsText = TextBox((10, y, -10, 22), "No letter repetitions")
        self.w.panel2.banRepetitions = CheckBox((10, y+22, -10, 22), "", value=self.prefs["ban_repetitions"])
        
        # Panel 3: Advanced Filters
        self.w.panel3 = Group((0, 0, -0, -0))
        y = 10
        self.w.panel3.matchPatternText = TextBox((10, y, -10, 22), "Match pattern (regex):")
        self.w.panel3.matchPatternEdit = EditText((10, y+22, -10, 22), self.prefs["match_pattern"])
        
        y += 54
        self.w.panel3.customCharsetText = TextBox((10, y, -10, 22), "Custom character set:")
        self.w.panel3.customCharsetEdit = EditText((10, y+22, -10, 22), self.prefs["custom_charset"])
        
        y += 54
        self.w.panel3.markGlyphsText = TextBox((10, y, -10, 22), "Mark found glyphs")
        self.w.panel3.markGlyphs = CheckBox((10, y+22, 100, 22), "", value=self.prefs.get("mark_glyphs", False))
        
        try:
            # Add color picker if available
            self.w.panel3.markColor = NoneTypeColorWell((120, y+22, -10, 22), 
                                                      callback=self._mark_color_callback, 
                                                      color=self.prefs.get("mark_color"))
        except:
            # Fallback if color picker not available
            self.w.panel3.markColorText = TextBox((120, y+22, -10, 22), "Color picker not available")
            
        y += 54
        self.w.panel3.helpButton = Button((10, y, -10, 22), "Regex Reference", callback=self._load_regex_reference)
        
        # Panel 4: Output Settings
        self.w.panel4 = Group((0, 0, -0, -0))
        y = 10
        self.w.panel4.caseText = TextBox((10, y, 100, 22), "Case:")
        self.w.panel4.case = PopUpButton((110, y, -10, 22), ["lowercase", "UPPERCASE", "Title Case", "RaNdOm"], callback=self._case_change_callback)
        
        y += 32
        self.w.panel4.sortByText = TextBox((10, y, 100, 22), "Sort by:")
        self.w.panel4.sortBy = PopUpButton((110, y, -10, 22), ["alphabetical", "length", "width"], callback=self._sort_change_callback)
        
        y += 32
        self.w.panel4.sortOrderText = TextBox((10, y, 100, 22), "Sort order:")
        self.w.panel4.sortOrder = PopUpButton((110, y, -10, 22), ["ascending", "descending"])
        
        y += 32
        self.w.panel4.outputFormatText = TextBox((10, y, 100, 22), "Output format:")
        self.w.panel4.outputFormat = PopUpButton((110, y, -10, 22), [item[0] for item in OUTPUT_FORMATS])
        
        y += 32
        self.w.panel4.saveToFileText = TextBox((10, y, 100, 22), "Save to file:")
        self.w.panel4.saveToFile = CheckBox((110, y, 22, 22), "", value=self.prefs.get("save_to_file", False), callback=self._toggle_save_file)
        self.w.panel4.savePathButton = Button((140, y, 60, 22), "Browse", callback=self._select_save_path)
        self.w.panel4.savePath = EditText((210, y, -10, 22), self.prefs.get("output_path", ""), readOnly=True)
        
        y += 32
        self.w.panel4.sampleText = TextBox((10, y, -10, 22), "Sample Text:")
        self.w.panel4.sampleTextArea = EditText((10, y+22, -10, 60), self.prefs.get("sample_text", ""), callback=self._sample_text_callback)
        
        # Set defaults for popups
        for i, language in enumerate(self.dictionaries.keys()):
            if language == self.prefs["language"]:
                self.w.panel1.source.set(i)
                break
        
        case_mapping = {"lowercase": 0, "uppercase": 1, "titlecase": 2, "random": 3}
        self.w.panel4.case.set(case_mapping.get(self.prefs["case_setting"].lower(), 0))
        
        sort_mapping = {"alphabetical": 0, "length": 1, "width": 2}
        self.w.panel4.sortBy.set(sort_mapping.get(self.prefs["sort_by"].lower(), 0))
        
        order_mapping = {"ascending": 0, "descending": 1}
        self.w.panel4.sortOrder.set(order_mapping.get(self.prefs["sort_order"].lower(), 0))
        
        # Set output format
        for i, (label, value) in enumerate(OUTPUT_FORMATS):
            if value == self.prefs.get("output_format", "space"):
                self.w.panel4.outputFormat.set(i)
                break
        
        # Enable/disable save path based on save to file checkbox
        self._toggle_ui_elements()
        
        # Create either accordion view (modern RoboFont) or tabs (older versions)
        if has_accordion:
            self.w.accordionView = AccordionView((0, 0, -0, -40),
                [
                    dict(label="Basic Settings", view=self.w.panel1, size=160, collapsed=False),
                    dict(label="Letter Filters", view=self.w.panel2, size=200, collapsed=False),
                    dict(label="Advanced Filters", view=self.w.panel3, size=180, collapsed=True),
                    dict(label="Output Settings", view=self.w.panel4, size=200, collapsed=True)
                ]
            )
        else:
            # Fallback UI for older RoboFont versions - use tabs instead
            self.w.tabs = Tabs((0, 0, -0, -40), 
                ["Basic", "Letters", "Advanced", "Output"],
                callback=self._tab_callback
            )
            self.w.tabs[0].setPosSize((0, 0, -0, -0))
            self.w.tabs[1].setPosSize((0, 0, -0, -0))
            self.w.tabs[2].setPosSize((0, 0, -0, -0))
            self.w.tabs[3].setPosSize((0, 0, -0, -0))
            
            # Add panels to tabs
            self.w.panel1.setPosSize((10, 10, -10, -10))
            self.w.panel2.setPosSize((10, 10, -10, -10))
            self.w.panel3.setPosSize((10, 10, -10, -10))
            self.w.panel4.setPosSize((10, 10, -10, -10))
            
            self.w.tabs[0].addSubview(self.w.panel1)
            self.w.tabs[1].addSubview(self.w.panel2)
            self.w.tabs[2].addSubview(self.w.panel3)
            self.w.tabs[3].addSubview(self.w.panel4)
        
        # Results area
        self.w.resultText = TextBox((10, -30, 70, 22), "Results:")
        self.w.resultsList = EditText((80, -30, -10, 22), "", readOnly=True)
        
        # Buttons
        self.w.cancelButton = Button((-90, -30, -10, 22), "Cancel", callback=self._cancel_callback)
        self.w.goButton = Button((-170, -30, -100, 22), "Make Words", callback=self._make_words_callback)
        
        # Set up font observer
        addObserver(self, "_font_closed", "fontDidClose")
        
        # Open window
        self.w.open()
    
    def _load_preferences(self) -> Dict:
        """Load the saved preferences or use defaults"""
        prefs = {}
        for key, default in DEFAULT_PREFS.items():
            if key in ["limit_to_charset", "required_letters_only", "ban_repetitions"]:
                prefs[key] = read_ext_default_boolean(key, default)
            else:
                prefs[key] = getExtensionDefault(f"{EXTENSION_KEY}.{key}", default)
        return prefs
    
    def _save_preferences(self) -> None:
        """Save the current settings as preferences"""
        # Get values from UI
        prefs = {
            "word_count": self._get_integer_value(self.w.panel1.countEdit),
            "min_length": self._get_integer_value(self.w.panel1.minLengthEdit),
            "max_length": self._get_integer_value(self.w.panel1.maxLengthEdit),
            "limit_to_charset": self.w.panel1.limitToCharset.get(),
            "required_letters": self.w.panel2.requiredLettersEdit.get(),
            "required_letters_only": self.w.panel2.requiredLettersOnly.get(),
            "ban_repetitions": self.w.panel2.banRepetitions.get(),
            "match_pattern": self.w.panel3.matchPatternEdit.get(),
            "custom_charset": self.w.panel3.customCharsetEdit.get(),
            "language": list(self.dictionaries.keys())[self.w.panel1.source.get()],
            "case_setting": ["lowercase", "uppercase", "titlecase", "random"][self.w.panel4.case.get()],
            "sort_by": ["alphabetical", "length", "width"][self.w.panel4.sortBy.get()],
            "sort_order": ["ascending", "descending"][self.w.panel4.sortOrder.get()],
            "output_format": OUTPUT_FORMATS[self.w.panel4.outputFormat.get()][1],
            "mark_glyphs": self.w.panel3.markGlyphs.get(),
            "mark_color": self.w.panel3.markColor.get(),
            "save_to_file": self.w.panel4.saveToFile.get(),
            "output_path": self.w.panel4.savePath.get(),
            "sample_text": self.w.panel4.sampleTextArea.get(),
            "load_preset": self.w.panel1.presets.get(),
            "save_preset": self.w.panel1.presets.get()
        }
        
        # Save to extension defaults
        for key, value in prefs.items():
            if key in ["limit_to_charset", "required_letters_only", "ban_repetitions"]:
                write_ext_default_boolean(key, value)
            else:
                setExtensionDefault(f"{EXTENSION_KEY}.{key}", value)
    
    def _get_integer_value(self, field):
        """Get an integer value from a text field, with fallback to 0"""
        try:
            return int(field.get())
        except (ValueError, TypeError):
            return 0
    
    def _toggle_limit_charset(self, sender):
        """Callback for toggling the limit to charset option"""
        is_limited = sender.get()
        font = CurrentFont()
        if is_limited and not font:
            ShowMessage("No font is open. The character set limit will have no effect.", title="No Font Open")
    
    def _change_source_callback(self, sender):
        """Callback for changing the dictionary source"""
        language_index = sender.get()
        language = list(self.dictionaries.keys())[language_index]
        self.prefs["language"] = language
    
    def _case_change_callback(self, sender):
        """Callback for changing the case setting"""
        case_index = sender.get()
        case_options = ["lowercase", "uppercase", "titlecase", "random"]
        self.prefs["case_setting"] = case_options[case_index]
    
    def _sort_change_callback(self, sender):
        """Callback for changing the sort method"""
        sort_index = sender.get()
        sort_options = ["alphabetical", "length", "width"]
        self.prefs["sort_by"] = sort_options[sort_index]
    
    def _load_regex_reference(self, sender):
        """Open a web page with regex reference"""
        webbrowser.open("https://docs.python.org/3/library/re.html")
    
    def _make_words_callback(self, sender):
        """Generate words based on the current settings"""
        # Get font
        font = CurrentFont()
        
        # Get filter parameters
        filter_params = {
            "min_length": self._get_integer_value(self.w.panel1.minLengthEdit),
            "max_length": self._get_integer_value(self.w.panel1.maxLengthEdit),
            "limit_to_charset": self.w.panel1.limitToCharset.get(),
            "required_letters": self.w.panel2.requiredLettersEdit.get(),
            "required_letters_only": self.w.panel2.requiredLettersOnly.get(),
            "ban_repetitions": self.w.panel2.banRepetitions.get(),
            "match_pattern": self.w.panel3.matchPatternEdit.get(),
            "custom_charset": self.w.panel3.customCharsetEdit.get(),
            "excluded_letters": self.w.panel2.excludedLettersEdit.get()
        }
        
        # Validate input
        is_valid, error_message = validate_input(filter_params, font)
        if not is_valid:
            ShowMessage(error_message, title="Input Error")
            return
        
        # Get output settings
        word_count = self._get_integer_value(self.w.panel1.countEdit)
        
        settings = {
            "word_count": word_count,
            "case_setting": ["lowercase", "uppercase", "titlecase", "random"][self.w.panel4.case.get()],
            "language": list(self.dictionaries.keys())[self.w.panel1.source.get()],
            "sort_by": ["alphabetical", "length", "width"][self.w.panel4.sortBy.get()],
            "sort_order": ["ascending", "descending"][self.w.panel4.sortOrder.get()],
            "output_format": OUTPUT_FORMATS[self.w.panel4.outputFormat.get()][1],
            "mark_glyphs": self.w.panel3.markGlyphs.get(),
            "mark_color": self.w.panel3.markColor.get(),
            "save_to_file": self.w.panel4.saveToFile.get(),
            "output_path": self.w.panel4.savePath.get(),
            "sample_text": self.w.panel4.sampleTextArea.get()
        }
        
        # Get dictionary path
        language = settings["language"]
        dictionary_path = self.dictionaries.get(language)
        
        if not dictionary_path or not os.path.exists(dictionary_path):
            ShowMessage(f"Dictionary for {language} not found.", title="Dictionary Error")
            return
        
        # Generate words
        words = generate_words(word_count, filter_params, settings, dictionary_path, font)
        
        # Show results
        if not words:
            ShowMessage("No words found matching your criteria. Try relaxing some constraints.", title="No Results")
            return
        
        # Format output
        output_format = settings["output_format"]
        result_text = format_output(words, output_format)
        
        # Display words
        self.w.resultsList.set(result_text)
        
        # Mark glyphs if requested
        if settings["mark_glyphs"] and font and settings["mark_color"]:
            marked_count = mark_glyphs_in_font(words, font, settings["mark_color"])
            ShowMessage(f"Marked {marked_count} glyphs in the font.", title="Marked Glyphs")
        
        # Save to file if requested
        if settings["save_to_file"] and settings["output_path"]:
            success = save_output_to_file(words, settings["output_path"], output_format)
            if success:
                ShowMessage(f"Words saved to {settings['output_path']}", title="File Saved")
            else:
                ShowMessage(f"Failed to save words to file.", title="File Error")
        
        # If a font is open, show words in Space Center
        if font and output_format != "spacecenter":
            OpenSpaceCenter(font, newWindow=True)
            sc = CurrentSpaceCenter()
            if sc:
                sc.setRaw(result_text)
        
        # Save preferences
        self._save_preferences()
    
    def _mark_color_callback(self, sender):
        """Callback for changing the mark color"""
        # Update color in preferences
        self.prefs["mark_color"] = sender.get()
    
    def _cancel_callback(self, sender):
        """Close the window"""
        self.w.close()
    
    def _font_closed(self, info):
        """Handle font closing event"""
        # Check if limiting to charset when no font is available
        if self.w.panel1.limitToCharset.get():
            all_fonts = AllFonts()
            if not all_fonts:
                self.w.panel1.limitToCharset.set(False)
                ShowMessage("Font closed. Character set limit has been disabled.", title="Font Closed")
    
    def windowCloseCallback(self, sender):
        """Clean up when window is closed"""
        removeObserver(self, "fontDidClose")
    
    def _tab_callback(self, sender):
        """Callback for tab changes - only used in older RoboFont versions"""
        pass

    def _load_preset_callback(self, sender):
        """Callback for loading a preset"""
        try:
            preset_index = sender.get()
            preset_name = list(self.presets.keys())[preset_index]
            preset_settings = self.presets[preset_name]
            
            # Update preferences with preset settings
            for key, value in preset_settings.items():
                if key in self.prefs:
                    self.prefs[key] = value
                    
            # Refresh the UI to reflect the loaded preset
            self._toggle_ui_elements()
            
            print(f"Loaded preset: {preset_name}")
        except Exception as e:
            print(f"Error loading preset: {e}")
    
    def _save_preset_callback(self, sender):
        """Callback for saving the current settings as a preset"""
        try:
            # Get current UI values
            current_settings = {
                "word_count": self._get_integer_value(self.w.panel1.countEdit),
                "min_length": self._get_integer_value(self.w.panel1.minLengthEdit),
                "max_length": self._get_integer_value(self.w.panel1.maxLengthEdit),
                "limit_to_charset": self.w.panel1.limitToCharset.get(),
                "required_letters": self.w.panel2.requiredLettersEdit.get(),
                "required_letters_only": self.w.panel2.requiredLettersOnly.get(),
                "excluded_letters": self.w.panel2.excludedLettersEdit.get(),
                "ban_repetitions": self.w.panel2.banRepetitions.get(),
                "match_pattern": self.w.panel3.matchPatternEdit.get(),
                "custom_charset": self.w.panel3.customCharsetEdit.get(),
                "mark_glyphs": self.w.panel3.markGlyphs.get(),
                "case_setting": ["lowercase", "uppercase", "titlecase", "random"][self.w.panel4.case.get()],
                "sort_by": ["alphabetical", "length", "width"][self.w.panel4.sortBy.get()],
                "sort_order": ["ascending", "descending"][self.w.panel4.sortOrder.get()],
                "output_format": OUTPUT_FORMATS[self.w.panel4.outputFormat.get()][1],
            }
            
            # Try to get mark color
            try:
                if hasattr(self.w.panel3, "markColor"):
                    current_settings["mark_color"] = self.w.panel3.markColor.get()
            except:
                pass
            
            # Get current preset name or create a new one
            preset_index = self.w.panel1.presets.get()
            preset_names = list(self.presets.keys())
            
            if preset_index < len(preset_names):
                preset_name = preset_names[preset_index]
                
                # Ask for confirmation before overwriting
                message_result = ShowMessage(
                    "Do you want to overwrite the existing preset?",
                    informative_text=f"Preset: {preset_name}",
                    title="Save Preset",
                    button_titles=["Cancel", "Save New", "Overwrite"]
                )
                
                if message_result == 0:  # Cancel
                    return
                elif message_result == 1:  # Save New
                    # Ask for a new preset name
                    preset_name = dialogs.getDefault(
                        message="Enter name for new preset:",
                        value="My Preset"
                    )
                    if not preset_name:
                        return
            else:
                # Ask for a new preset name
                preset_name = dialogs.getDefault(
                    message="Enter name for new preset:",
                    value="My Preset"
                )
                if not preset_name:
                    return
            
            # Save the preset
            save_preset(preset_name, current_settings)
            print(f"Saved preset: {preset_name}")
            
            # Refresh preset list
            self.presets = load_presets()
            self.w.panel1.presets.setItems(list(self.presets.keys()))
            
            # Select the saved preset
            if preset_name in self.presets:
                preset_index = list(self.presets.keys()).index(preset_name)
                self.w.panel1.presets.set(preset_index)
                
        except Exception as e:
            print(f"Error saving preset: {e}")
            ShowMessage(
                "Failed to save preset",
                informative_text=f"Error: {e}",
                title="Error"
            )
    
    def _import_wordlist_callback(self, sender):
        """Callback for importing a word list"""
        try:
            path = import_wordlist()
            if path:
                # Update dictionaries list
                self.dictionaries = load_dictionaries()
                self.w.panel1.source.setItems(list(self.dictionaries.keys()))
                
                # Set the imported dictionary as current
                language_name = os.path.basename(path)
                language_name = os.path.splitext(language_name)[0]
                
                if language_name in self.dictionaries:
                    language_index = list(self.dictionaries.keys()).index(language_name)
                    self.w.panel1.source.set(language_index)
                    self.prefs["language"] = language_name
                    
                ShowMessage("Word list imported successfully", title="Import Successful")
        except Exception as e:
            print(f"Error importing word list: {e}")
            ShowMessage(
                "Failed to import word list",
                informative_text=f"Error: {e}",
                title="Error"
            )
    
    def _toggle_save_file(self, sender):
        """Callback for toggling the save to file option"""
        is_saving = sender.get()
        self.prefs["save_to_file"] = is_saving
        self._toggle_ui_elements()
    
    def _select_save_path(self, sender):
        """Callback for selecting a save path"""
        try:
            path = getFile(title="Select Save Path", messageText="Choose a file to save the output.")
            if path:
                self.w.panel4.savePath.set(path)
                self.prefs["output_path"] = path
        except Exception as e:
            print(f"Error selecting save path: {e}")
            # Fallback - let user enter path directly
            self.w.panel4.savePath.setReadOnly(False)
            self.w.panel4.savePath.set("")
            ShowMessage("Please enter the save path manually.", title="File Dialog Failed")
    
    def _sample_text_callback(self, sender):
        """Callback for updating sample text"""
        self.prefs["sample_text"] = sender.get()
    
    def _toggle_ui_elements(self):
        """Enable or disable UI elements based on current settings"""
        # RoboFont Vanilla implementation might not have setEnabled() for all UI elements
        # Use enable()/disable() instead
        if self.prefs["save_to_file"]:
            try:
                self.w.panel4.savePathButton.enable(True)
            except AttributeError:
                pass
                
            try:
                self.w.panel4.savePath.enable(True)
            except AttributeError:
                pass
        else:
            try:
                self.w.panel4.savePathButton.enable(False)
            except AttributeError:
                pass
                
            try:
                self.w.panel4.savePath.enable(False)
            except AttributeError:
                pass
                
        # Update UI based on preset
        preset_name = list(self.presets.keys())[self.w.panel1.presets.get()]
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            
            # Update all UI elements with values from preset
            try:
                # Basic settings
                self.w.panel1.countEdit.set(preset.get("word_count", DEFAULT_PREFS["word_count"]))
                self.w.panel1.minLengthEdit.set(preset.get("min_length", DEFAULT_PREFS["min_length"]))
                self.w.panel1.maxLengthEdit.set(preset.get("max_length", DEFAULT_PREFS["max_length"]))
                self.w.panel1.limitToCharset.set(preset.get("limit_to_charset", DEFAULT_PREFS["limit_to_charset"]))
                
                # Letter filters
                self.w.panel2.requiredLettersEdit.set(preset.get("required_letters", DEFAULT_PREFS["required_letters"]))
                self.w.panel2.requiredLettersOnly.set(preset.get("required_letters_only", DEFAULT_PREFS["required_letters_only"]))
                self.w.panel2.excludedLettersEdit.set(preset.get("excluded_letters", DEFAULT_PREFS["excluded_letters"]))
                self.w.panel2.banRepetitions.set(preset.get("ban_repetitions", DEFAULT_PREFS["ban_repetitions"]))
                
                # Advanced filters
                self.w.panel3.matchPatternEdit.set(preset.get("match_pattern", DEFAULT_PREFS["match_pattern"]))
                self.w.panel3.customCharsetEdit.set(preset.get("custom_charset", DEFAULT_PREFS["custom_charset"]))
                self.w.panel3.markGlyphs.set(preset.get("mark_glyphs", DEFAULT_PREFS["mark_glyphs"]))
                
                # Try to set mark color if the UI element exists and has a set method
                if hasattr(self.w.panel3, "markColor") and hasattr(self.w.panel3.markColor, "set"):
                    self.w.panel3.markColor.set(preset.get("mark_color", DEFAULT_PREFS["mark_color"]))
            except Exception as e:
                print(f"Error updating UI from preset: {e}")


# Entry point for the extension
def main():
    """Main function that starts the extension"""
    WordCreatorWindow()

if __name__ == "__main__":
    main() 