"""
Wood Shadow — Inside / Outside cuts with the double square box.

Recipe reverse-engineered from 250730_WoodShadow_{inside,outside}.otf:

    box    = x boxLeft..boxRight , y BOX_BOTTOM..BOX_TOP
    letter = shifted so boxLeft lands on SHIFT
    frame  = two rects, hollow, (OUTER-INNER) units thick:
               outer = box grown by OUTER on all four sides
               inner = box grown by INNER on all four sides
    advance = box width + 2*SHIFT

    Inside  = "Wood" layer   + frame
    Outside = default layer  + frame

Both cuts get the SAME box, taken from the shadow — that is what makes the two
fonts overlay. The "Shadow Square" layer is Nell's record of the shadow's own
bounding box, so where it is current the two agree exactly; where the shadow has
been redrawn since, the union keeps the frame around the letter instead of
through it.

No GSUB: the .ssNN alternates just ride along in the glyph order, as in the
2025 files.
"""

from fontTools.pens.transformPen import TransformPen

SHIFT = 15          # x of the box's left edge in the exported glyph
OUTER = 6           # frame outer edge, outside the box
INNER = 4           # frame inner edge, outside the box
BOX_BOTTOM = -13
BOX_TOP = 983

SQUARE_LAYER = "Shadow Square"
INSIDE_LAYER = "Wood"
OUTSIDE_LAYER = None        # None = the font's default layer

CUTS = [
    ("Inside", INSIDE_LAYER),
    ("Outside", OUTSIDE_LAYER),
]


def base_name(name):
    """G.ss02.ss01 -> G  (strip every .ssNN suffix)"""
    parts = name.split(".")
    keep = [parts[0]]
    for p in parts[1:]:
        if not (p.startswith("ss") and p[2:].isdigit()):
            keep.append(p)
    return ".".join(keep)


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
    """(left, right) of the box: the Shadow Square unioned with the shadow's own
    outline. None if the glyph gets no frame."""
    square = _square_rect(font, name)
    shadow = _shadow_rect(font, name)
    if square and shadow:
        return min(square[0], shadow[0]), max(square[1], shadow[1])
    return square or shadow


def draw_frame(pen, left, right):
    """Hollow rect frame around a box left..right, BOX_BOTTOM..BOX_TOP."""
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


def source_layer(font, layer_name):
    if layer_name is None:
        return font.getLayer(font.defaultLayerName)
    return font.getLayer(layer_name)


def build_cut(font, layer_name, style_name, report=None):
    """Return a new fontParts font holding one cut. Caller generates/saves it."""
    from fontParts.world import NewFont

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

        # unicodes from wherever they are defined
        uni = srcGlyph.unicodes
        if not uni and name in default:
            uni = default[name].unicodes
        g.unicodes = uni

    dst.glyphOrder = names
    return dst


def build(font, directory, cuts=None, report=None):
    """Generate the OTFs. Returns list of written paths."""
    import os

    written = []
    for style_name, layer_name in (cuts or CUTS):
        cut = build_cut(font, layer_name, style_name, report=report)
        family = (cut.info.familyName or "WoodShadow").replace(" ", "")
        path = os.path.join(directory, "%s-%s.otf" % (family, style_name))
        try:
            cut.generate("otfcff", path)
        except Exception:
            cut.generate(path=path, format="otf")
        cut.close()
        written.append(path)
    return written
