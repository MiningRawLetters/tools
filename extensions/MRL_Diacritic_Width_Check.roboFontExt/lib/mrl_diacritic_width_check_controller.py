# MRL Diacritic Width Check Controller
# Developed by Kevin Kuhn (Mining Raw Letters)

"""
UI for the MRL Diacritic Width Check extension.

Scans the current font's composite (diacritic) glyphs and lists any whose
advance width doesn't match their base letter's width - regardless of
whether the composite is built with components or with added contours.
"""

import logging
from vanilla import Window, List, Button, CheckBox, TextBox, EditText

try:
    from mojo.roboFont import CurrentFont
    from mojo.UI import Message
    from mojo.events import addObserver, removeObserver
except ImportError as import_error:
    logging.error(f"Required RoboFont modules not available: {import_error}")
    raise

try:
    from mojo.roboFont import OpenGlyphWindow
except ImportError:
    OpenGlyphWindow = None

from mrl_diacritic_width_check_utils import analyze_font_diacritic_widths


COLUMNS = [
    {"title": "Glyph", "key": "name", "width": 110},
    {"title": "Width", "key": "width", "width": 60},
    {"title": "Base", "key": "base", "width": 110},
    {"title": "Base Width", "key": "base_width", "width": 80},
    {"title": "Diff", "key": "diff", "width": 60},
]


class MRL_DiacriticWidthCheckController:

    def __init__(self):
        self.font = CurrentFont()
        self.all_results = []
        self.unresolved = []
        self.observers_added = False

        self.create_main_window()
        self.add_observers()
        self.rescan(None)

    def create_main_window(self):
        self.w = Window(
            (620, 480),
            "MRL Diacritic Width Check",
            minSize=(480, 320),
        )

        self.w.font_name = TextBox((10, 10, -10, 20), "No font open", sizeStyle="small")

        self.w.tolerance_label = TextBox((10, 36, 70, 20), "Tolerance:", sizeStyle="small")
        self.w.tolerance_value = EditText((80, 34, 50, 22), "0", callback=self.rescan)
        self.w.only_mismatches = CheckBox(
            (140, 34, 160, 22), "Only show mismatches",
            value=True, callback=self.rescan, sizeStyle="small",
        )
        self.w.rescan_button = Button((-100, 34, -10, 22), "Rescan", callback=self.rescan)

        self.w.results_list = List(
            (10, 66, -10, -60),
            [],
            columnDescriptions=COLUMNS,
            allowsSorting=True,
            doubleClickCallback=self.open_selected_glyph,
        )

        self.w.status = TextBox((10, -46, -10, 20), "Ready", sizeStyle="small")
        self.w.unresolved_status = TextBox((10, -26, -10, 20), "", sizeStyle="small")

        self.w.open()

    def add_observers(self):
        if not self.observers_added:
            addObserver(self, "fontDidOpen", "fontDidOpen")
            addObserver(self, "fontDidClose", "fontDidClose")
            addObserver(self, "fontBecameCurrent", "fontBecameCurrent")
            self.observers_added = True

    def remove_observers(self):
        if self.observers_added:
            removeObserver(self, "fontDidOpen")
            removeObserver(self, "fontDidClose")
            removeObserver(self, "fontBecameCurrent")
            self.observers_added = False

    def get_tolerance(self) -> int:
        try:
            return int(self.w.tolerance_value.get())
        except (ValueError, TypeError):
            return 0

    def rescan(self, sender):
        self.font = CurrentFont()

        if self.font is None:
            self.w.font_name.set("No font open")
            self.w.results_list.set([])
            self.w.status.set("No font open")
            self.w.unresolved_status.set("")
            return

        self.w.font_name.set(f"{self.font.info.familyName} {self.font.info.styleName}")

        tolerance = self.get_tolerance()
        analysis = analyze_font_diacritic_widths(self.font, tolerance=tolerance)
        self.all_results = analysis["results"]
        self.unresolved = analysis["unresolved"]

        only_mismatches = self.w.only_mismatches.get()
        rows = [r for r in self.all_results if r["mismatch"]] if only_mismatches else self.all_results
        self.w.results_list.set(rows)

        mismatch_count = sum(1 for r in self.all_results if r["mismatch"])
        self.w.status.set(
            f"{len(self.all_results)} composite glyphs checked, {mismatch_count} width mismatch(es)"
        )

        if self.unresolved:
            names = ", ".join(u["name"] for u in self.unresolved[:8])
            more = "..." if len(self.unresolved) > 8 else ""
            self.w.unresolved_status.set(
                f"{len(self.unresolved)} unresolved (base glyph missing): {names}{more}"
            )
        else:
            self.w.unresolved_status.set("")

    def open_selected_glyph(self, sender):
        selection = sender.getSelection()
        if not selection or self.font is None:
            return

        row = sender[selection[0]]
        glyph_name = row["name"]
        if glyph_name not in self.font:
            return

        if OpenGlyphWindow is not None:
            try:
                OpenGlyphWindow(self.font[glyph_name])
                return
            except Exception as error:
                logging.error(f"Could not open glyph window for '{glyph_name}': {error}")

        Message(f"Could not open a glyph window for '{glyph_name}' in this RoboFont version.")

    # Observer methods
    def fontDidOpen(self, notification):
        self.rescan(None)

    def fontDidClose(self, notification):
        self.rescan(None)

    def fontBecameCurrent(self, notification):
        self.rescan(None)

    def __del__(self):
        self.remove_observers()
