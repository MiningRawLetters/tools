import os

import vanilla
from mojo.UI import GetFolder
from fontParts.world import AllFonts

import wood_shadow_build as builder


class WoodShadowExport:

    def __init__(self):
        self.fonts = AllFonts()
        self.directory = None

        self.w = vanilla.Window((420, 230), "MRL Wood Shadow")

        self.w.fontLabel = vanilla.TextBox((15, 18, 60, 20), "Source")
        self.w.font = vanilla.PopUpButton(
            (80, 16, -15, 20),
            [f.info.familyName and "%s %s" % (f.info.familyName, f.info.styleName)
             or os.path.basename(f.path or "Untitled") for f in self.fonts],
        )

        self.w.cutsLabel = vanilla.TextBox((15, 52, 60, 20), "Cuts")
        self.w.inside = vanilla.CheckBox((80, 50, 120, 20), "Inside (Wood)", value=True)
        self.w.outside = vanilla.CheckBox((210, 50, -15, 20), "Outside (Shadow)", value=True)

        self.w.boxLabel = vanilla.TextBox((15, 86, 60, 20), "Box")
        self.w.box = vanilla.PopUpButton(
            (80, 84, 200, 20),
            ["Square ∪ shadow (recommended)", "Shadow Square only"],
        )

        self.w.dirButton = vanilla.Button((80, 118, 120, 20), "Output…",
                                          callback=self.chooseDirectory)
        self.w.dirLabel = vanilla.TextBox((210, 121, -15, 20), "—", sizeStyle="small")

        self.w.report = vanilla.TextBox((15, 150, -15, 70), "", sizeStyle="small")

        self.w.generate = vanilla.Button((-135, -35, 120, 20), "Generate",
                                         callback=self.generate)
        self.w.setDefaultButton(self.w.generate)

        if self.fonts:
            f = self.fonts[0]
            if f.path:
                self.setDirectory(os.path.dirname(f.path))
        else:
            self.w.generate.enable(False)
            self.w.report.set("No open fonts.")

        self.w.open()

    def setDirectory(self, directory):
        self.directory = directory
        self.w.dirLabel.set(os.path.basename(directory) or directory)

    def chooseDirectory(self, sender):
        directory = GetFolder("Where should the OTFs go?")
        if directory:
            self.setDirectory(directory)

    def generate(self, sender):
        if not self.directory:
            self.w.report.set("Pick an output folder first.")
            return

        font = self.fonts[self.w.font.get()]

        cuts = []
        if self.w.inside.get():
            cuts.append(("Inside", builder.INSIDE_LAYER))
        if self.w.outside.get():
            cuts.append(("Outside", builder.OUTSIDE_LAYER))
        if not cuts:
            self.w.report.set("Tick at least one cut.")
            return

        missing = [name for style, name in cuts
                   if name is not None and name not in font.layerOrder]
        if missing:
            self.w.report.set("Missing layer(s): %s" % ", ".join(missing))
            return

        mode = [builder.BOX_UNION, builder.BOX_SQUARE][self.w.box.get()]

        report = []
        try:
            written = builder.build(font, self.directory, cuts=cuts,
                                    mode=mode, report=report)
        except Exception as error:
            self.w.report.set("Failed: %s" % error)
            raise

        lines = ["Wrote %s" % ", ".join(os.path.basename(p) for p in written)]
        for kind in ("unboxed (no square)", "overflows frame"):
            hit = [r.split(": ")[-1] for r in report if r.startswith(kind)]
            if hit:
                lines.append("%s: %s" % (kind, ", ".join(sorted(set(hit)))))
        self.w.report.set("\n".join(lines))


WoodShadowExport()
