# Installation Guide - MRL Glyph Dimensions

## Quick Installation

1. **Download the Extension**
   - Download the `MRL_Glyph_Dimensions.roboFontExt` folder
   - Keep the folder structure intact

2. **Install in RoboFont**
   - Double-click the `MRL_Glyph_Dimensions.roboFontExt` folder
   - RoboFont will automatically install the extension
   - You may need to restart RoboFont

3. **Access the Extension**
   - Open RoboFont
   - Go to **Scripts** menu
   - Select **MRL Glyph Dimensions**

## Manual Installation

If the automatic installation doesn't work:

1. **Locate RoboFont Extensions Folder**
   - Open RoboFont
   - Go to **RoboFont** → **Preferences**
   - Click on **Extensions** tab
   - Note the **Extensions Folder** path

2. **Copy Extension**
   - Copy the `MRL_Glyph_Dimensions.roboFontExt` folder
   - Paste it into the Extensions Folder

3. **Restart RoboFont**
   - Close RoboFont completely
   - Reopen RoboFont
   - The extension should now appear in the Scripts menu

## Verification

To verify the installation:

1. **Check Extension List**
   - Go to **RoboFont** → **Preferences** → **Extensions**
   - Look for "MRL Glyph Dimensions" in the list
   - Status should show as "Enabled"

2. **Test Functionality**
   - Open a font in RoboFont
   - Go to **Scripts** → **MRL Glyph Dimensions**
   - The extension window should open and display font information

## Troubleshooting

### Extension Not Appearing
- Ensure the folder structure is intact
- Check that all files are present in the `lib` folder
- Restart RoboFont completely
- Check RoboFont's error log for any issues

### Import Errors
- Verify RoboFont version is 4.0 or later
- Check that Python 3.x is available
- Ensure all required dependencies are installed

### UI Issues
- Check that Vanilla framework is available
- Verify macOS version compatibility
- Try resetting RoboFont preferences

## Requirements

- **RoboFont**: Version 4.0 or later
- **macOS**: 10.14 or later
- **Python**: 3.x (included with RoboFont)
- **Dependencies**: Vanilla, FontParts, Defcon (included with RoboFont)

## Support

If you encounter issues:

1. **Check the Error Log**
   - Go to **Window** → **Extension Manager**
   - Look for any error messages

2. **Test the Extension**
   - Run the test script: `test_extension.py`
   - Check for any failed tests

3. **Contact Support**
   - **Developer**: Kevin Kuhn
   - **Website**: https://miningrawletters.com
   - **GitHub**: https://github.com/KevinKuhn997

## Uninstallation

To remove the extension:

1. **Via Extension Manager**
   - Go to **RoboFont** → **Preferences** → **Extensions**
   - Find "MRL Glyph Dimensions"
   - Click "Remove" or "Disable"

2. **Manual Removal**
   - Navigate to the Extensions Folder
   - Delete the `MRL_Glyph_Dimensions.roboFontExt` folder
   - Restart RoboFont

## Updates

To update the extension:

1. **Remove Old Version**
   - Follow the uninstallation steps above

2. **Install New Version**
   - Follow the installation steps above
   - The new version will replace the old one

## File Structure

```
MRL_Glyph_Dimensions.roboFontExt/
├── info.plist                 # Extension metadata
├── README.md                  # Documentation
├── INSTALL.md                 # This file
├── test_extension.py          # Test script
└── lib/                       # Python modules
    ├── __init__.py
    ├── main.py                # Entry point
    ├── mrl_glyph_dimensions_controller.py  # Main controller
    └── mrl_glyph_dimensions_utils.py       # Utility functions
``` 