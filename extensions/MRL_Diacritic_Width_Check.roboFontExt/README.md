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

The list also shows each glyph's left/right sidebearing next to its base's,
for context on where a width mismatch comes from.

## Use

1. Open the extension from RoboFont's Extensions menu (or Window menu, per `preferredName`).
2. It scans the current font automatically; re-run with "Rescan" after edits.
3. Set a tolerance (units) if you want to ignore rounding-level differences.
4. Double-click a row to open that glyph directly - useful for the mismatches
   that need a manual fix rather than a sidebearing match (e.g. a reversed E
   built from real outline changes, not spacing).
5. Select one or more rows (multi-select works) and click **Match Left**,
   **Match Right**, or **Match Both** to move that glyph's left sidebearing,
   change its right sidebearing, or both, to match the base glyph's. These
   are independent because the fix isn't always symmetric - some glyphs only
   need one side moved.
   - Match Left shifts the whole glyph and grows/shrinks the width to hit
     the target left margin; the right margin is unaffected.
   - Match Right only changes the width to hit the target right margin; the
     left margin is unaffected.
   - Match Both does not necessarily make the widths equal - a composite's
     own ink (an accent mark, `dcroat`'s bar) can be wider than the base's,
     so matching both margins can still leave a different advance width.
     That's expected, not a bug.
   Matched glyphs get a green square in the first column and stay in the
   list (even under "Only show mismatches") so you can see what was just
   changed, until the font is closed/switched.
6. The `L`/`R` cells are directly editable - click into one, type a new
   value, press Enter, and it's applied straight to the glyph (same
   left/right semantics as the match buttons above) without touching the
   base at all. Useful when neither side should match the base exactly.
7. The status line below the list flags composites whose base glyph couldn't
   be found in the font (usually a missing/renamed base).

Note: hook-letters like `Bhook`/`Dhook`/`Istroke` are flagged too since they're
built the same "component + drawn addition" way - their different margins may
be intentional (the hook needs room). Selection is deliberate here rather
than a bulk auto-fix: check each mismatch before matching it, don't select-all.
