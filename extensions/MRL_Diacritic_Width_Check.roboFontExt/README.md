# MRL Diacritic Width Check

RoboFont extension for Waitomo (and any UFO with a similar build pattern).

Scans the current font and, for every composite/diacritic glyph, compares its
advance width to its base letter's width - regardless of whether the
composite is pure components (e.g. `Aacute` = `A` + `acutecmb.uc`) or a
component plus a hand-drawn addition (e.g. `dcroat` = `d` component + a drawn
bar contour, `Istroke`, `Bhook`, `itilde`...).

## How base-glyph detection works

The base letter is always the glyph's **first component**. A composite only
qualifies for the check if every component after the first is a combining
mark (name contains `cmb`) - this is how Waitomo names its mark glyphs
(`acutecmb.uc`, `brevecmb_gravecmb`, etc.).

Excluded on purpose:
- mark glyphs themselves (name contains `cmb`)
- ligatures (name contains `_`, e.g. `f_f`, `j_l`, per this project's naming convention)
- glyphs built from two+ real-letter/figure components (`ij`, `zerocircle`, `oneeighth`...) - not a base+accessory relationship
- glyphs with no components at all (standalone letterforms like `eng`, `dhook`)

## Use

1. Open the extension from RoboFont's Extensions menu (or Window menu, per `preferredName`).
2. It scans the current font automatically; re-run with "Rescan" after edits.
3. Set a tolerance (units) if you want to ignore rounding-level differences.
4. Double-click a row to open that glyph.
5. The status line below the list flags composites whose base glyph couldn't
   be found in the font (usually a missing/renamed base).

Note: hook-letters like `Bhook`/`Dhook`/`Istroke` are flagged too since they're
built the same "component + drawn addition" way - their wider width may be
intentional (the hook needs room), so treat those rows as a prompt to confirm,
not an automatic bug.
