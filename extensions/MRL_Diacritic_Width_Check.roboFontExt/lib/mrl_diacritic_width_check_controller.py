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
    from mojo.UI import Message, OpenGlyphWindow
    from mojo.events import addObserver, removeObserver
except ImportError as import_error:
    logging.error(f"Required RoboFont modules not available: {import_error}")
    raise

from mrl_diacritic_width_check_utils import (
    analyze_font_diacritic_widths,
    match_glyph_left_to_base,
    match_glyph_right_to_base,
    match_glyph_both_to_base,
)


# A colored-square emoji renders reliably as plain text in any vanilla.List
# cell. An NSImage value does NOT auto-render as an icon in this vanilla
# version - it gets stringified and, in a narrow column, shows only "...".
MATCHED_MARK = "\U0001F7E9"  # green square


COLUMNS = [
    {"title": "", "key": "matched_mark", "width": 22},
    {"title": "Glyph", "key": "name", "width": 100},
    {"title": "Width", "key": "width", "width": 55},
    {"title": "L", "key": "left", "width": 45, "editable": True},
    {"title": "R", "key": "right", "width": 45, "editable": True},
    {"title": "Base", "key": "base", "width": 100},
    {"title": "Base W", "key": "base_width", "width": 60},
    {"title": "Base L", "key": "base_left", "width": 55},
    {"title": "Base R", "key": "base_right", "width": 55},
    {"title": "Diff", "key": "diff", "width": 50},
]


class MRL_DiacriticWidthCheckController:

    def __init__(self):
        self.font = CurrentFont()
        self.all_results = []
        self.unresolved = []
        self.recently_matched = set()
        self._last_font_path = None
        self.observers_added = False

        self.create_main_window()
        self.add_observers()
        self.rescan(None)

    def create_main_window(self):
        self.w = Window(
            (720, 500),
            "MRL Diacritic Width Check",
            minSize=(560, 320),
        )

        self.w.font_name = TextBox((10, 10, -10, 20), "No font open", sizeStyle="small")

        self.w.tolerance_label = TextBox((10, 36, 70, 20), "Tolerance:", sizeStyle="small")
        self.w.tolerance_value = EditText((80, 34, 50, 22), "0", callback=self.rescan)
        self.w.only_mismatches = CheckBox(
            (140, 34, 160, 22), "Only show mismatches",
            value=True, callback=self.rescan, sizeStyle="small",
        )
        self.w.rescan_button = Button((-100, 34, -10, 22), "Rescan", callback=self.rescan)

        self.w.match_left_button = Button(
            (10, 62, 90, 22), "Match Left",
            callback=self.match_left_to_base,
        )
        self.w.match_right_button = Button(
            (104, 62, 90, 22), "Match Right",
            callback=self.match_right_to_base,
        )
        self.w.match_both_button = Button(
            (198, 62, 90, 22), "Match Both",
            callback=self.match_both_to_base,
        )
        self.w.match_hint = TextBox(
            (296, 64, -10, 20),
            "Match sidebearing(s) to base, or edit L/R directly. Double-click a row to open that glyph.",
            sizeStyle="small",
        )

        self.w.results_list = List(
            (10, 92, -10, -60),
            [],
            columnDescriptions=COLUMNS,
            allowsSorting=True,
            allowsMultipleSelection=True,
            doubleClickCallback=self.open_selected_glyph,
            editCallback=self.list_edited,
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

        # Only clear the "just matched" highlight when the font itself actually
        # changes - not on every notification RoboFont fires (fontBecameCurrent
        # also fires from routine glyph edits, e.g. right after a match).
        current_path = self.font.path
        if current_path != self._last_font_path:
            self.recently_matched = set()
            self._last_font_path = current_path

        tolerance = self.get_tolerance()
        analysis = analyze_font_diacritic_widths(self.font, tolerance=tolerance)
        self.all_results = analysis["results"]
        self.unresolved = analysis["unresolved"]

        only_mismatches = self.w.only_mismatches.get()
        if only_mismatches:
            rows = [r for r in self.all_results if r["mismatch"] or r["name"] in self.recently_matched]
        else:
            rows = list(self.all_results)

        for row in rows:
            row["matched_mark"] = MATCHED_MARK if row["name"] in self.recently_matched else ""

        self.w.results_list.set(rows)

        mismatch_count = sum(1 for r in self.all_results if r["mismatch"])
        self.w.status.set(
            f"{len(self.all_results)} composite glyphs checked, {mismatch_count} width mismatch(es)"
        )

        if self.unresolved:
            names = ", ".join(u["name"] for u in self.unresolved)
            self.w.unresolved_status.set(
                f"{len(self.unresolved)} unresolved (base glyph missing): {names}"
            )
        else:
            self.w.unresolved_status.set("")

    def _apply_match(self, match_func, label):
        if self.font is None:
            Message("No font is currently open.")
            return

        selection = self.w.results_list.getSelection()
        if not selection:
            Message("Select one or more rows first.")
            return

        rows = [self.w.results_list[i] for i in selection]
        matched = 0
        for row in rows:
            if match_func(self.font, row["name"], row["base"]):
                matched += 1
                self.recently_matched.add(row["name"])

        if matched:
            self.font.changed()

        self.w.status.set(f"Matched {matched} glyph(s) - {label}")
        self.rescan(None)

    def match_left_to_base(self, sender):
        self._apply_match(match_glyph_left_to_base, "left sidebearing")

    def match_right_to_base(self, sender):
        self._apply_match(match_glyph_right_to_base, "right sidebearing")

    def match_both_to_base(self, sender):
        self._apply_match(match_glyph_both_to_base, "both sidebearings")

    def list_edited(self, sender):
        """
        Fires after any cell finishes editing. vanilla doesn't tell us which
        row/column changed, so compare every visible row's L/R against the
        glyph's actual current margins and apply whichever differ.
        """
        if self.font is None:
            return

        edited_names = set()
        for row in sender.get():
            name = row.get("name")
            if not name or name not in self.font:
                continue
            glyph = self.font[name]

            new_left = self._as_float(row.get("left"))
            if new_left is not None and glyph.leftMargin is not None and round(glyph.leftMargin, 1) != new_left:
                glyph.leftMargin = new_left
                edited_names.add(name)

            new_right = self._as_float(row.get("right"))
            if new_right is not None and glyph.rightMargin is not None and round(glyph.rightMargin, 1) != new_right:
                glyph.rightMargin = new_right
                edited_names.add(name)

        if not edited_names:
            return

        self.recently_matched.update(edited_names)
        self.font.changed()
        self.w.status.set(f"Manually edited {len(edited_names)} glyph(s)")
        self.rescan(None)

    @staticmethod
    def _as_float(value):
        try:
            return round(float(value), 1)
        except (TypeError, ValueError):
            return None

    def open_selected_glyph(self, sender):
        selection = sender.getSelection()
        if not selection or self.font is None:
            return

        row = sender[selection[0]]
        glyph_name = row["name"]
        if glyph_name not in self.font:
            return

        try:
            OpenGlyphWindow(self.font[glyph_name])
        except Exception as error:
            logging.error(f"Could not open glyph window for '{glyph_name}': {error}")
            Message(f"Could not open a glyph window for '{glyph_name}': {error}")

    # Observer methods
    def fontDidOpen(self, notification):
        self.rescan(None)

    def fontDidClose(self, notification):
        self.rescan(None)

    def fontBecameCurrent(self, notification):
        self.rescan(None)

    def __del__(self):
        self.remove_observers()
