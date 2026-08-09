"""
Wood Shadow — generate the Inside and Outside cuts with the double square box.

Run in RoboFont's scripting panel with the Wood Shadow UFO as the current font.
Set the options just below, hit Run. Leave OUTPUT_DIR as None and it asks.

Recipe, reverse-engineered from 250730_WoodShadow_{inside,outside}.otf:

    box    = x boxLeft..boxRight , y BOX_BOTTOM..BOX_TOP
    letter = shifted so boxLeft lands at x = SHIFT
    frame  = two hollow rects, (OUTER-INNER) units thick
               outer = box grown by OUTER on all four sides
               inner = box grown by INNER on all four sides
    advance = box width + 2*SHIFT

    Inside  = "Wood" layer           + frame
    Outside = default (SHADOW) layer + frame

Both cuts get the SAME box, measured from the shadow — that is what makes the
two fonts overlay. The "Shadow Square" layer is Nell's record of the shadow's
own bounding box, so the box is the union of the two: where the square is still
current they agree exactly and the 2025 files are reproduced to the unit; where
the shadow has been redrawn since, the frame stays around the letter instead of
cutting through it.

No GSUB is built — the .ssNN alternates ride along in the glyph order, as in
the 2025 files.
"""

# ---------------------------------------------------------------- options ---

MAKE_INSIDE = True
MAKE_OUTSIDE = True

MAKE_UFO = True             # save a .ufo per cut
MAKE_OTF = True             # generate an .otf per cut

OUTPUT_DIR = None           # None = ask; or "/path/to/folder"

# ------------------------------------------------------------- the recipe ---

SHIFT = 15          # x of the box's left edge in the exported glyph
OUTER = 6           # frame outer edge, outside the box
INNER = 4           # frame inner edge, outside the box
BOX_BOTTOM = -13
BOX_TOP = 983

SQUARE_LAYER = "Shadow Square"
INSIDE_LAYER = "Wood"
OUTSIDE_LAYER = None        # None = the font's default layer

# -----------------------------------------------------------------------------

import os

from fontTools.pens.transformPen import TransformPen
from fontParts.world import CurrentFont, NewFont


def base_name(name):
    """G.ss02.ss01 -> G  (strip every .ssNN suffix)"""
    parts = name.split(".")
    keep = [parts[0]]
    for p in parts[1:]:
        if not (p.startswith("ss") and p[2:].isdigit()):
            keep.append(p)
    return ".".join(keep)


def source_layer(font, layer_name):
    if layer_name is None:
        return font.getLayer(font.defaultLayerName)
    return font.getLayer(layer_name)


def _square_rect(font, name):
    try:
        square = font.getLayer(SQUARE_LAYER)
    except Exception:
        return None
    for candidate in (name, base_name(name)):
        if candidate in square:
            return 0.0, float(square[candidate].width)
    return None


def _shadow_rect(font, name):
    shadow = source_layer(font, OUTSIDE_LAYER)
    for candidate in (name, base_name(name)):
        if candidate in shadow:
            bounds = shadow[candidate].bounds
            if bounds:
                return float(bounds[0]), float(bounds[2])
    return None


def box_rect(font, name):
    """(left, right) of the box: Shadow Square unioned with the shadow's own
    outline. None if neither exists — the glyph then gets no frame."""
    square = _square_rect(font, name)
    shadow = _shadow_rect(font, name)
    if square and shadow:
        return min(square[0], shadow[0]), max(square[1], shadow[1])
    return square or shadow


def draw_frame(pen, left, right):
    y0, y1 = BOX_BOTTOM, BOX_TOP

    # inner rect, clockwise
    pen.moveTo((right + INNER, y1 + INNER))
    pen.lineTo((right + INNER, y0 - INNER))
    pen.lineTo((left - INNER, y0 - INNER))
    pen.lineTo((left - INNER, y1 + INNER))
    pen.closePath()

    # outer rect, counter-clockwise
    pen.moveTo((right + OUTER, y1 + OUTER))
    pen.lineTo((left - OUTER, y1 + OUTER))
    pen.lineTo((left - OUTER, y0 - OUTER))
    pen.lineTo((right + OUTER, y0 - OUTER))
    pen.closePath()


def build_cut(font, layer_name, style_name, report=None):
    """A new font holding one cut. Caller saves and/or generates it."""
    src = source_layer(font, layer_name)
    dst = NewFont(showInterface=False)

    dst.info.unitsPerEm = font.info.unitsPerEm
    dst.info.ascender = font.info.ascender
    dst.info.descender = font.info.descender
    dst.info.capHeight = font.info.capHeight
    dst.info.xHeight = font.info.xHeight
    dst.info.familyName = font.info.familyName or "Wood Shadow"
    dst.info.styleName = style_name

    names = [n for n in font.glyphOrder if n in src] or sorted(src.keys())
    default = font.getLayer(font.defaultLayerName)

    for name in names:
        srcGlyph = src[name]
        g = dst.newGlyph(name)
        rect = box_rect(font, name)

        if rect is None:
            srcGlyph.draw(TransformPen(g.getPen(), (1, 0, 0, 1, SHIFT, 0)))
            g.width = srcGlyph.width
            if report is not None and len(srcGlyph):
                report.append("unboxed (no box): %s" % name)
        else:
            left, right = rect
            offset = SHIFT - left
            pen = g.getPen()
            srcGlyph.draw(TransformPen(pen, (1, 0, 0, 1, offset, 0)))
            letter = g.bounds
            draw_frame(pen, left + offset, right + offset)
            g.width = (right - left) + 2 * SHIFT
            if report is not None and letter:
                if letter[0] < SHIFT - INNER or letter[2] > SHIFT + (right - left) + INNER:
                    report.append("overflows frame: %s" % name)

        uni = srcGlyph.unicodes
        if not uni and name in default:
            uni = default[name].unicodes
        g.unicodes = uni

    dst.glyphOrder = names
    return dst


def build(font, directory, cuts=None, ufo=True, otf=True, report=None):
    """Write the cuts. Returns the list of paths written."""
    if cuts is None:
        cuts = []
        if MAKE_INSIDE:
            cuts.append(("Inside", INSIDE_LAYER))
        if MAKE_OUTSIDE:
            cuts.append(("Outside", OUTSIDE_LAYER))

    written = []
    for style_name, layer_name in cuts:
        cut = build_cut(font, layer_name, style_name, report=report)
        stem = "%s-%s" % ((cut.info.familyName or "WoodShadow").replace(" ", ""),
                          style_name)

        if ufo:
            path = os.path.join(directory, stem + ".ufo")
            cut.save(path)
            written.append(path)

        if otf:
            path = os.path.join(directory, stem + ".otf")
            try:
                cut.generate("otfcff", path)
            except Exception:
                cut.generate(path=path, format="otf")
            written.append(path)

        cut.close()
    return written


def main():
    font = CurrentFont()
    if font is None:
        print("Open the Wood Shadow UFO first.")
        return

    if not (MAKE_INSIDE or MAKE_OUTSIDE):
        print("Nothing to do — switch on MAKE_INSIDE and/or MAKE_OUTSIDE.")
        return

    if not (MAKE_UFO or MAKE_OTF):
        print("Nothing to write — switch on MAKE_UFO and/or MAKE_OTF.")
        return

    if MAKE_INSIDE and INSIDE_LAYER not in font.layerOrder:
        print('No "%s" layer in this font.' % INSIDE_LAYER)
        return

    directory = OUTPUT_DIR
    if directory is None:
        from mojo.UI import GetFolder
        directory = GetFolder("Where should the Wood Shadow files go?")
        if not directory:
            print("Cancelled.")
            return

    report = []
    written = build(font, directory, ufo=MAKE_UFO, otf=MAKE_OTF, report=report)

    print("Wood Shadow — wrote %s file(s) to %s" % (len(written), directory))
    for path in written:
        print("   %s" % os.path.basename(path))

    for kind in ("unboxed (no box)", "overflows frame"):
        hits = sorted(set(r.split(": ")[-1] for r in report if r.startswith(kind)))
        if hits:
            print("   %s: %s" % (kind, ", ".join(hits)))


main()
