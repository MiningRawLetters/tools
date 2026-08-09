# MRL Diacritic Width Check Utilities
# Developed by Kevin Kuhn (Mining Raw Letters)

"""
Detects the base letter a composite/diacritic glyph is built on and compares
its advance width against that base letter's width.

Waitomo builds composites two ways, both handled by the same rule:
  - component-based:  Aacute      = A + acutecmb.uc
  - contour-added:     dcroat      = d (component) + a drawn bar (contour)
In both cases the true base letter is always the FIRST component in the
glyph's outline, and any accessory components are combining marks whose
base glyph name contains "cmb" (e.g. acutecmb.uc, brevecmb_gravecmb).

Glyphs that are excluded on purpose (not a "letter + diacritic" composite):
  - combining mark glyphs themselves (name contains "cmb")
  - ligatures (name contains "_", e.g. f_f, j_l) - different-glyph sequences,
    not a base + accessory relationship
  - glyphs built from two or more real-letter/figure components where the
    non-first components are NOT marks (ligatures like "ij", fraction/circled
    figures like "zerocircle", "oneeighth") - these fail the "rest are marks"
    test and are skipped
  - glyphs with no components at all (standalone letterforms such as eng,
    dhook - not composed from another base letter)
"""

from typing import Any, Dict, List, Optional


def is_mark_glyph_name(name: Optional[str]) -> bool:
    """True if a glyph name identifies a combining-mark glyph, not a letter."""
    return bool(name) and "cmb" in name


def is_ligature_glyph_name(name: str) -> bool:
    """Waitomo/MRL convention: ligature glyph names contain an underscore."""
    return "_" in name


def find_base_component_name(glyph) -> Optional[str]:
    """
    Return the base-letter glyph name a composite glyph is built on, or None
    if the glyph isn't a qualifying letter+diacritic composite.
    """
    components = list(glyph.components)
    if not components:
        return None

    first_base = components[0].baseGlyph
    if not first_base or is_mark_glyph_name(first_base):
        return None

    accessory_bases = [c.baseGlyph for c in components[1:]]
    if not all(is_mark_glyph_name(b) for b in accessory_bases):
        # Extra non-mark components -> ligature or figure composite, skip.
        return None

    return first_base


def analyze_font_diacritic_widths(font, tolerance: int = 0) -> Dict[str, List[Dict[str, Any]]]:
    """
    Walk every glyph in `font` and compare composite glyphs' widths against
    their base letter's width.

    Returns a dict with two lists:
      'results'    - every qualifying composite, width-matched or not
      'unresolved' - composites whose base glyph name isn't in the font
    """
    results: List[Dict[str, Any]] = []
    unresolved: List[Dict[str, Any]] = []

    for name in font.keys():
        glyph = font[name]

        if is_mark_glyph_name(name) or is_ligature_glyph_name(name):
            continue

        base_name = find_base_component_name(glyph)
        if base_name is None:
            continue

        if base_name == name:
            continue

        if base_name not in font:
            unresolved.append({
                "name": name,
                "width": glyph.width,
                "base": base_name,
                "unicode": glyph.unicode,
            })
            continue

        base_glyph = font[base_name]
        diff = glyph.width - base_glyph.width

        results.append({
            "name": name,
            "width": round(glyph.width),
            "left": round(glyph.leftMargin, 1),
            "right": round(glyph.rightMargin, 1),
            "base": base_name,
            "base_width": round(base_glyph.width),
            "base_left": round(base_glyph.leftMargin, 1),
            "base_right": round(base_glyph.rightMargin, 1),
            "diff": round(diff, 1),
            "mismatch": abs(diff) > tolerance,
            "unicode": glyph.unicode,
        })

    results.sort(key=lambda r: (-abs(r["diff"]), r["name"]))
    unresolved.sort(key=lambda r: r["name"])

    return {"results": results, "unresolved": unresolved}


def _resolve_pair(font, glyph_name: str, base_name: str):
    if glyph_name not in font or base_name not in font:
        return None, None
    return font[glyph_name], font[base_name]


def match_glyph_left_to_base(font, glyph_name: str, base_name: str) -> bool:
    """
    Move `glyph_name`'s outline so its left sidebearing matches `base_name`'s.
    fontParts' leftMargin setter shifts the whole glyph and grows/shrinks the
    width by the same amount, so the right sidebearing is left untouched.
    """
    glyph, base = _resolve_pair(font, glyph_name, base_name)
    if glyph is None:
        return False
    glyph.leftMargin = base.leftMargin
    return True


def match_glyph_right_to_base(font, glyph_name: str, base_name: str) -> bool:
    """
    Change `glyph_name`'s width so its right sidebearing matches `base_name`'s.
    fontParts' rightMargin setter only changes width, never moves the outline,
    so the left sidebearing is left untouched.
    """
    glyph, base = _resolve_pair(font, glyph_name, base_name)
    if glyph is None:
        return False
    glyph.rightMargin = base.rightMargin
    return True


def match_glyph_both_to_base(font, glyph_name: str, base_name: str) -> bool:
    """
    Match both sidebearings to the base's. Left first (moves the outline,
    preserves the current right margin), then right (only adjusts width) -
    so both land exactly on the base's values regardless of order-sensitivity.

    Note this is NOT the same as matching advance width: the composite's own
    outline (e.g. dcroat's extra bar, an accent mark) can be wider than the
    base's, so matching both margins can still leave a different width - that
    difference is real ink, not spacing drift.
    """
    glyph, base = _resolve_pair(font, glyph_name, base_name)
    if glyph is None:
        return False
    glyph.leftMargin = base.leftMargin
    glyph.rightMargin = base.rightMargin
    return True
