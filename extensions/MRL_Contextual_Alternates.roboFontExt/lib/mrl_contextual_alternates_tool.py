# MRL Contextual Alternates
# Developed by Kevin Kuhn (Mining Raw Letters)

import re
from collections import defaultdict
from mojo.roboFont import CurrentFont
import vanilla
from mojo.UI import *
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *
from mojo.events import addObserver, removeObserver
from vanilla.dialogs import message

class MRLContextualAlternatesController(BaseWindowController):
    
    def __init__(self):
        self.font = CurrentFont()
        self.font_analysis = {}
        
        # Window setup
        self.w = FloatingWindow((500, 400), "MRL Contextual Alternates", minSize=(450, 350))
        
        # Current font display
        self.w.fontLabel = TextBox((20, 20, -20, 20), f"Font: {self.font.info.familyName if self.font and self.font.info.familyName else 'No font open'}")
        
        # Analyze button
        self.w.analyzeButton = Button((20, 50, 120, 30), "Analyze Font", callback=self.analyzeFont)
        
        # Preview area
        self.w.previewLabel = TextBox((20, 90, -20, 20), "Feature Preview:")
        self.w.preview = TextEditor((20, 115, -20, 200), readOnly=True)
        
        # Apply button
        self.w.applyButton = Button((20, 330, 120, 30), "Apply to Font", callback=self.generateAndApply)
        self.w.applyButton.enable(False)
        
        # Status
        self.w.status = TextBox((160, 335, -20, 20), "Ready")
        
        # Add observer for font changes
        addObserver(self, "fontChanged", "fontDidOpen")
        addObserver(self, "fontChanged", "fontDidClose")
        
        self.w.open()
        
        # Auto-analyze if font is open
        if self.font:
            self.analyzeFont(None)
        
    def fontChanged(self, notification):
        """Update when font changes"""
        self.font = CurrentFont()
        font_name = self.font.info.familyName if self.font and self.font.info.familyName else "No font open"
        self.w.fontLabel.set(f"Font: {font_name}")
        
        if self.font:
            self.analyzeFont(None)
        else:
            self.w.preview.set("")
            self.w.applyButton.enable(False)
            self.w.status.set("No font open")

    def analyzeFont(self, sender):
        """Analyze the current font for alternates"""
        if not self.font:
            self.w.status.set("No font open")
            return
        
        self.w.status.set("Analyzing font...")
        self.font_analysis = {}
        
        # Find all base characters and their alternates
        base_chars = {}
        
        for glyph_name in self.font.keys():
            # Handle single letter characters
            if '.' not in glyph_name:
                # This is potentially a base character - include single letters, numbers and special chars
                base_chars[glyph_name] = {
                    'base': glyph_name,
                    'alternates': []
                }
                
                # Look for alternates (.ss01, .ss02, .ss03)
                for suffix in ['.ss01', '.ss02', '.ss03']:
                    alt_name = f"{glyph_name}{suffix}"
                    if alt_name in self.font:
                        base_chars[glyph_name]['alternates'].append(alt_name)
        
        # Categorize characters - keep ALL characters together for global cycling
        categories = {
            'All_Characters': {
                'base_chars': [],
                'alternates': {'Alt1': [], 'Alt2': [], 'Alt3': []},
                'valid_alts': set()
            }
        }
        
        for char, data in base_chars.items():
            if data['alternates']:  # Only include characters that have alternates
                categories['All_Characters']['base_chars'].append(data['base'])
                
                # Check which alternates exist
                if len(data['alternates']) >= 1:
                    categories['All_Characters']['alternates']['Alt1'].append(data['alternates'][0])
                    categories['All_Characters']['valid_alts'].add('Alt1')
                if len(data['alternates']) >= 2:
                    categories['All_Characters']['alternates']['Alt2'].append(data['alternates'][1])
                    categories['All_Characters']['valid_alts'].add('Alt2')
                if len(data['alternates']) >= 3:
                    categories['All_Characters']['alternates']['Alt3'].append(data['alternates'][2])
                    categories['All_Characters']['valid_alts'].add('Alt3')
        
        # Store organized data
        for category_name, category_data in categories.items():
            self.font_analysis[category_name] = {
                'classes': {
                    'Base': category_data['base_chars'],
                    'Alt1': category_data['alternates']['Alt1'],
                    'Alt2': category_data['alternates']['Alt2'],
                    'Alt3': category_data['alternates']['Alt3']
                },
                'valid_alts': category_data['valid_alts']
            }
        
        # Generate preview
        preview_text = self.generateFeaturePreview()
        self.w.preview.set(preview_text)
        
        if self.font_analysis:
            self.w.applyButton.enable(True)
            self.w.status.set(f"Analysis complete - found {len(categories['All_Characters']['base_chars'])} characters with alternates")
        else:
            self.w.applyButton.enable(False)
            self.w.status.set("No alternates found")

    def generateFeaturePreview(self):
        """Generate a preview of the feature code"""
        if not self.font_analysis:
            return "No analysis data available"
        
        return self.generateFeatureCode()

    def generateFeatureCode(self):
        """Generate efficient OpenType feature code with lookback distance of 10 characters"""
        if not self.font_analysis:
            return "# No analysis data available"
        
        output = [
            "# MRL Contextual Alternates - Extended Lookback Distance",
            "# Character-specific cycling with 10-character lookback",
            ""
        ]
        
        # Get all characters with alternates
        all_chars_data = self.font_analysis.get('All_Characters', {})
        base_glyphs = all_chars_data.get('classes', {}).get('Base', [])
        
        if not base_glyphs:
            return "# No characters with alternates found"
        
        # Collect character data efficiently
        char_data = {}
        all_glyphs = []
        
        # Group characters by type for reporting
        letters = []
        numbers = []
        special_chars = []
        
        for base_char in base_glyphs:
            alts = []
            if f"{base_char}.ss01" in self.font:
                alts.append(f"{base_char}.ss01")
            if f"{base_char}.ss02" in self.font:
                alts.append(f"{base_char}.ss02")
            if f"{base_char}.ss03" in self.font:
                alts.append(f"{base_char}.ss03")
            
            if alts:
                char_data[base_char] = alts
                all_glyphs.append(base_char)
                all_glyphs.extend(alts)
                
                # Categorize the character
                if len(base_char) == 1 and base_char.isalpha():
                    letters.append(base_char)
                elif len(base_char) == 1 and base_char.isdigit():
                    numbers.append(base_char)
                elif base_char in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "zero"]:
                    numbers.append(base_char)
                elif base_char not in ["space"]:
                    special_chars.append(base_char)
        
        # Add transparent characters
        transparent_chars = []
        for glyph_name in ["space", "period", "comma", "question", "exclam", "colon", "semicolon", "hyphen", "endash", "emdash"]:
            if glyph_name in self.font:
                transparent_chars.append(glyph_name)
        
        all_glyphs.extend(transparent_chars)
        
        # Generate compact class definitions
        output.append("# Universal character class for lookback")
        output.append(f"@AllChars = [{' '.join(all_glyphs)}];")
        output.append("")
        
        # Add character type statistics
        output.append(f"# Character analysis: {len(letters)} letters, {len(numbers)} numbers, {len(special_chars)} special characters")
        if letters:
            output.append(f"# Letters: {' '.join(sorted(letters))}")
        if numbers:
            output.append(f"# Numbers: {' '.join(sorted(numbers))}")
        if special_chars:
            output.append(f"# Special: {' '.join(sorted(special_chars))}")
        output.append("")
        
        output.append("feature calt {")
        
        # Generate rules with lookback of 10 characters
        for char, alts in char_data.items():
            output.append(f"    # {char} cycling rules - 10 character lookback")
            
            # Generate rules for 1-10 character distances
            for distance in range(1, 11):  # 1 to 10 characters
                context = " @AllChars" * (distance - 1)  # Build the context string
                
                # BASE + ... + BASE -> BASE + ... + ALT1
                output.append(f"    sub {char}{context} {char}' by {alts[0]};")
                
                if len(alts) > 1:
                    # ALT1 + ... + BASE -> ALT1 + ... + ALT2
                    output.append(f"    sub {alts[0]}{context} {char}' by {alts[1]};")
                    
                    if len(alts) > 2:
                        # ALT2 + ... + BASE -> ALT2 + ... + ALT3
                        output.append(f"    sub {alts[1]}{context} {char}' by {alts[2]};")
                        # ALT3 + ... + BASE -> ALT3 + ... + BASE (cycle back)
                        output.append(f"    sub {alts[2]}{context} {char}' by {char};")
                    else:
                        # ALT2 + ... + BASE -> ALT2 + ... + BASE (cycle back for 2-alt systems)
                        output.append(f"    sub {alts[1]}{context} {char}' by {char};")
                else:
                    # Single alternate - simple toggle
                    output.append(f"    sub {alts[0]}{context} {char}' by {char};")
            
            output.append("")
        
        output.append("} calt;")
        output.append("")
        output.append(f"# Generated for {len(char_data)} characters")
        output.append("# Lookback: 10 characters maximum")
        output.append("# This should handle most real-world text cases")
        output.append(f"# Total rules: approximately {len(char_data) * 10 * (len(alts) + 1)} lines")
        output.append("# End of MRL Contextual Alternates")
        
        return "\n".join(output)
    
    def generateAndApply(self, sender):
        """Generate and apply the contextual alternates to the font"""
        if not self.font or not self.font_analysis:
            return
        
        self.w.status.set("Applying to font...")
        
        feature_code = self.generateFeatureCode()
        
        # Apply to font features
        if hasattr(self.font, 'features'):
            current_features = self.font.features.text or ""
            
            # Remove existing calt feature if present
            feature_pattern = re.compile(r'feature calt\s*\{.*?\}\s*calt;', re.DOTALL)
            current_features = feature_pattern.sub('', current_features)
            
            # Ensure languagesystem statement exists
            if 'languagesystem DFLT dflt;' not in current_features:
                current_features = 'languagesystem DFLT dflt;\n\n' + current_features
            
            # Add new calt feature
            self.font.features.text = current_features + '\n\n' + feature_code
            self.font.changed()
            
            message("Success!", f"Character-specific contextual alternates applied to {self.font.info.familyName or 'font'}!\n\nEach character now cycles independently based on previous occurrences.")
            self.w.status.set("Contextual alternates applied successfully")
        else:
            message("Error", "Could not access font features.")

# Create and show the controller
MRLContextualAlternatesController() 