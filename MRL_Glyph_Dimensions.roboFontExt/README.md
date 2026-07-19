# MRL Glyph Dimensions

A comprehensive RoboFont extension for managing glyph dimensions including horizontal and vertical metrics.

**Developed by Kevin Kuhn (Mining Raw Letters)**

## Features

### Horizontal Metrics Management
- **Individual Glyph Control**: Set width, left sidebearing, and right sidebearing for the currently selected glyph
- **Batch Operations**: Apply uniform horizontal metrics to all glyphs in the font
- **Preset Configurations**: Quick access to common width configurations (900, 1000 units)

### Vertical Metrics Management
- **Font-Level Control**: Set units per em, ascender, descender, cap height, and x-height
- **Webfont Strategy**: Apply cross-platform consistent vertical metrics for web fonts
- **Real-time Display**: See current font metrics at a glance

### User Interface
- **Live Updates**: Interface updates automatically when fonts or glyphs change
- **Status Feedback**: Clear status messages for all operations
- **Error Handling**: Robust error handling with user-friendly messages

## Installation

1. Download the `MRL_Glyph_Dimensions.roboFontExt` folder
2. Double-click the extension to install it in RoboFont
3. Restart RoboFont if necessary
4. Access the extension from the **Scripts** menu → **MRL Glyph Dimensions**

## Usage

### Getting Started
1. Open a font in RoboFont
2. Launch the MRL Glyph Dimensions extension
3. The interface will display current font information and metrics

### Horizontal Metrics

#### Individual Glyph Operations
- Select a glyph in the font window
- Enter desired values in the Width, Left SB, or Right SB fields
- Click "Apply" to update the selected glyph

#### Batch Operations
- Enter target width and left sidebearing values
- Click "Apply to All Glyphs" to update all glyphs in the font
- The extension preserves outline widths while adjusting sidebearings

#### Presets
- **900 Width**: Sets width=900, left=90 (preserves 90-unit right sidebearing)
- **1000 Width**: Sets width=1000, left=100 (preserves 100-unit right sidebearing)

### Vertical Metrics

#### Individual Settings
- Modify units per em, ascender, descender, cap height, or x-height individually
- Click "Apply" for each setting to update the font

#### Webfont Strategy
- Click "Apply Webfont Strategy" to set all vertical metrics for cross-platform consistency
- This applies the same values to sTypo, hhea, and win metrics
- Sets the 'useTypoMetrics' flag for improved consistency

#### Webfont Preset
- Click "Webfont" preset to apply recommended webfont values:
  - Units per em: 1000
  - Ascender: 810
  - Descender: -90
  - Cap height: 720
  - X-height: 500

## Technical Details

### Horizontal Metrics Logic
The extension preserves outline widths when applying batch horizontal operations:
```
outline_width = current_width - left_sb - right_sb
new_right_sb = target_width - new_left_sb - outline_width
```

### Vertical Metrics Strategy
The webfont strategy applies consistent metrics across platforms:
- **sTypo metrics**: For modern applications
- **hhea metrics**: For macOS/Linux
- **win metrics**: For Windows (with positive descent value)

### Error Handling
- Validates font and glyph selection before operations
- Provides clear error messages for invalid inputs
- Gracefully handles missing or empty glyphs

## Requirements

- RoboFont 4.0 or later
- Python 3.x
- macOS (RoboFont requirement)

## Development

This extension follows the MRL coding standards:
- Functional/declarative programming paradigm
- Comprehensive error handling
- Type hints for better code clarity
- Observer pattern for UI updates
- Modular design for maintainability

## Version History

### v1.0
- Initial release
- Horizontal metrics management
- Vertical metrics management
- Batch operations
- Preset configurations
- Real-time UI updates

## Support

For issues, questions, or feature requests, please contact:
- **Developer**: Kevin Kuhn
- **Website**: https://miningrawletters.com
- **GitHub**: https://github.com/KevinKuhn997

## License

This extension is developed by Kevin Kuhn (Mining Raw Letters) and follows the same licensing terms as other MRL tools. 