# MRL Wood Shadow

Generates the **Inside** and **Outside** cuts of Wood Shadow, each with the
double square box drawn around the letter. Replaces the lost 2025 script;
the geometry was reverse-engineered from
`MRL Typefaces/Wood Shadow/WoodShadow OTFs/250730_WoodShadow_{inside,outside}.otf`.

## The recipe

```
box    = x boxLeft..boxRight , y -13..983
letter = shifted so boxLeft lands at x = 15
frame  = two hollow rects, 2 units thick
           outer = box + 6 on all four sides
           inner = box + 4 on all four sides
advance = box width + 30        (9 units clear each side of the frame)

Inside  = "Wood" layer          + frame
Outside = default (SHADOW) layer + frame
```

Both cuts get the **same** box, measured from the shadow — that is what lets
the two fonts overlay. No GSUB is built: the `.ssNN` alternates ride along in
the glyph order, as in the 2025 files.

## Where the box comes from

The `Shadow Square` layer is Nell's record of the shadow's own bounding box —
in the 2025 files the two coincide to within a unit. Since then a number of
glyphs have been redrawn and their shadow now extends past the recorded square
(`G` 918 vs 768, `two` 802 vs 687, `question.ss01` 770 vs 537), so the square
alone would cut the frame straight through the letter.

So the box is the **union of the Shadow Square and the drawn shadow outline**.
That reproduces the 2025 files exactly wherever the square is current,
self-corrects where it isn't, and never clips. Glyphs with no square of their
own fall back to their base glyph's (`G.ss02.ss01` → `G`) before the union.

A glyph only ends up unframed if *neither* source has anything — currently just
`ampersand`, whose shadow is still an empty outline with a tracing image in it.
Those are listed in the report, along with anything that still overflows.

## Install

```bash
cp -R "MRL_WoodShadow.roboFontExt" ~/Library/Application\ Support/RoboFont/plugins/
```

Restart RoboFont, then **Extensions → MRL Wood Shadow**. Pick the source font,
tick the cuts, choose an output folder, Generate.

## Files

- `lib/main.py` — the dialog
- `lib/wood_shadow_build.py` — the build, importable on its own
  (`build(font, directory)`); all constants at the top
