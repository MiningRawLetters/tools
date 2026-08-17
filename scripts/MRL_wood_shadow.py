"""
Wood Shadow — generate the Inside and Outside cuts with the double square box.

Run in RoboFont's scripting panel with the Wood Shadow UFO as the current font.
Set the options just below, hit Run. Leave OUTPUT_DIR as None and it asks.

Recipe, reverse-engineered from 250730_WoodShadow_{inside,outside}.otf:

    box    = x boxLeft..boxRight , y from the shadow "O"
    letter = shifted so boxLeft lands at x = SHIFT
    frame  = two hollow rects, (OUTER-INNER) units thick
               outer = box grown by OUTER on all four sides
               inner = box grown by INNER on all four sides
    advance = box width + 2*SHIFT

    Inside  = "Wood" layer           + frame
    Outside = default (SHADOW) layer + frame

Vertically the box is ONE pair of lines for the whole font: the top and bottom
of the SHADOW layer's REFERENCE_GLYPH ("O"), whose overshoot sets the band every
other glyph is boxed against. Same lines on every glyph, both cuts.

Horizontally the box is per glyph, measured from the shadow — that is what makes
the two cuts overlay, since the Wood letter sits inset within it. If the font
still has a "Shadow Square" layer (Nell's older record of the shadow's own
bounding box) it is unioned in; without it, the drawn shadow alone decides.

No GSUB is built — the .ssNN alternates ride along in the glyph order, as in
the 2025 files.
"""

# ---------------------------------------------------------------- options ---

MAKE_INSIDE = True
MAKE_OUTSIDE = True

MAKE_UFO = True             # save a .ufo per cut
MAKE_OTF = True             # generate an .otf per cut

OUTPUT_DIR = None           # None = ask. The picker has a New Folder button;
                            # the folder you choose is the folder used, no
                            # extra level added. Or set "/path/to/folder".

OUTPUT_SUBFOLDER = None     # normally None: write straight into that folder.
                            # Give it a name to nest one level — strftime codes
                            # are filled in, e.g. "%y%m%d_WoodShadow" ->
                            # 260817_WoodShadow. Made if missing.

# ------------------------------------------------------------- the recipe ---

SHIFT = 15          # x of the box's left edge in the exported glyph
OUTER = 6           # frame outer edge, outside the box
INNER = 4           # frame inner edge, outside the box

REFERENCE_GLYPH = "O"       # its shadow outline sets the box top and bottom
BOX_FALLBACK = (-13, 983)   # only if that glyph is missing or empty

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


def box_vertical(font):
    """(bottom, top) of the box: the shadow O's own extremes, overshoot and all.
    One pair of lines for the whole font, both cuts."""
    shadow = source_layer(font, OUTSIDE_LAYER)
    if REFERENCE_GLYPH in shadow:
        bounds = shadow[REFERENCE_GLYPH].bounds
        if bounds:
            return float(bounds[1]), float(bounds[3])
    print('   ! no usable "%s" in the shadow layer — box height falls back to %s'
          % (REFERENCE_GLYPH, BOX_FALLBACK))
    return BOX_FALLBACK


def draw_frame(pen, left, right, y0, y1):
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


def build_cut(font, layer_name, style_name, vertical=None, report=None):
    """A new font holding one cut. Caller saves and/or generates it."""
    src = source_layer(font, layer_name)
    bottom, top = vertical or box_vertical(font)
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
            draw_frame(pen, left + offset, right + offset, bottom, top)
            g.width = (right - left) + 2 * SHIFT
            if report is not None and letter:
                if (letter[0] < SHIFT - INNER
                        or letter[2] > SHIFT + (right - left) + INNER
                        or letter[1] < bottom - INNER
                        or letter[3] > top + INNER):
                    report.append("overflows frame: %s" % name)

        uni = srcGlyph.unicodes
        if not uni and name in default:
            uni = default[name].unicodes
        g.unicodes = uni

    dst.glyphOrder = names
    return dst


def ask_where():
    """Pick the folder to write into. A plain folder picker, except with the
    New Folder button switched on — so making a folder is a choice, not a
    thing that happens to you."""
    try:
        from AppKit import NSOpenPanel
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseFiles_(False)
        panel.setCanChooseDirectories_(True)
        panel.setCanCreateDirectories_(True)
        panel.setAllowsMultipleSelection_(False)
        panel.setTitle_("Wood Shadow")
        panel.setMessage_("Where should the Wood Shadow files go? "
                          "Use New Folder if you want one.")
        panel.setPrompt_("Write here")
        if panel.runModal() != 1:      # NSModalResponseOK
            return None
        return panel.URL().path()
    except ImportError:
        from mojo.UI import GetFolder
        return GetFolder("Where should the Wood Shadow files go?")


def make_directory(directory, subfolder=None):
    """The folder to write into, made if it isn't there — nested paths included."""
    if subfolder:
        import time
        directory = os.path.join(directory, time.strftime(subfolder))
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return directory


def build(font, directory, cuts=None, ufo=True, otf=True, subfolder=None,
          report=None):
    """Write the cuts. Returns the list of paths written."""
    if cuts is None:
        cuts = []
        if MAKE_INSIDE:
            cuts.append(("Inside", INSIDE_LAYER))
        if MAKE_OUTSIDE:
            cuts.append(("Outside", OUTSIDE_LAYER))

    directory = make_directory(directory, subfolder)

    vertical = box_vertical(font)
    print("   box band from %s: y %s..%s" % (REFERENCE_GLYPH, vertical[0], vertical[1]))

    written = []
    for style_name, layer_name in cuts:
        cut = build_cut(font, layer_name, style_name, vertical=vertical,
                        report=report)
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
        directory = ask_where()
        if not directory:
            print("Cancelled.")
            return

    report = []
    written = build(font, directory, ufo=MAKE_UFO, otf=MAKE_OTF,
                    subfolder=OUTPUT_SUBFOLDER, report=report)

    print("Wood Shadow — wrote %s file(s) to %s"
          % (len(written), os.path.dirname(written[0]) if written else directory))
    for path in written:
        print("   %s" % os.path.basename(path))

    for kind in ("unboxed (no box)", "overflows frame"):
        hits = sorted(set(r.split(": ")[-1] for r in report if r.startswith(kind)))
        if hits:
            print("   %s: %s" % (kind, ", ".join(hits)))


main()
