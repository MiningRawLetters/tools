# MRL Batch Test Install Extension

A streamlined RoboFont extension for batch test installing multiple UFO files at once.

## Features

- **Batch Test Install**: Install multiple UFO files with a single click
- **Drag & Drop**: Add UFO files by dragging them into the list
- **Add Open UFO**: Quickly add all currently open UFO files to the batch
- **Clean Interface**: Simple, focused design without unnecessary clutter
- **Smart UFO Management**: Handles already-open UFO files without closing them

## Installation

1. Copy the `MRL_Batch_Test_Install.roboFontExt` folder to your RoboFont plugins directory:
   ```
   ~/Library/Application Support/RoboFont/plugins/
   ```
2. Restart RoboFont
3. Access via **File → MRL Batch Test Install...**

## Usage

1. **Add UFO files**:
   - Click the **+** button to browse and select UFO files
   - Click **Add Open UFO** to add all currently open UFO files
   - Drag and drop UFO files directly into the list

2. **Test Install**:
   - Click **Test Install All** to batch install all UFO files
   - Already-open UFO files remain open after installation
   - Newly-opened UFO files are automatically closed after installation

3. **Manage List**:
   - Select files and click **-** to remove them
   - Click **Clear All** to empty the entire list
   - Delete key also removes selected files

## Supported Formats

- `.ufo` (UFO files)
- `.designspace` (Designspace files)
- `.otf` (OpenType fonts)
- `.ttf` (TrueType fonts)

## Notes

- Test installed fonts are temporary and will be removed when RoboFont closes
- The extension intelligently handles already-open UFO files without disrupting your workflow
- Compact interface focuses on the essential batch test install functionality

## Version

**1.0** - Initial release with streamlined interface

## Developer

Created by **Kevin Kuhn** (Mining Raw Letters) 