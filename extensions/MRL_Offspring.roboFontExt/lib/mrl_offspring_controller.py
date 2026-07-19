# MRL Offspring Controller
# Developed by Kevin Kuhn (Mining Raw Letters)
#
# Creates named, saved copies of open UFOs on disk (new file name + optional
# new style name in font info; family name is kept). The original open font
# is never touched - each copy is made with shutil.copytree before anything
# is renamed.
#
# Flow: pick a parent font, click "+ Add" to append an editable row for it
# (as many times as you like, even switching parent in between), then
# Create Offspring processes every row in the table.

import os
import shutil
from mojo.roboFont import AllFonts, OpenFont
from mojo.UI import Message
from mojo.events import addObserver, removeObserver
from vanilla import Window, List, Button, TextBox, PopUpButton


class MRL_OffspringController:

    def __init__(self):
        self.fonts = AllFonts()
        if not self.fonts:
            Message("No fonts open.")
            return

        self.rows = []
        self.counters = {}

        self.w = Window((760, 480), "MRL Offspring")

        self.w.info = TextBox(
            (10, 10, -10, 34),
            "Every font deserves offspring: pick a parent UFO, add as many named copies "
            "as you like, then create them. Family name is kept; originals are untouched."
        )

        self.w.parentLabel = TextBox((10, 54, 55, 20), "Parent:")
        self.w.parentPopup = PopUpButton((65, 52, -110, 22), self.fontLabels())
        self.w.addButton = Button((-100, 52, 90, 22), "+ Add", callback=self.addRow)

        columnDescriptions = [
            {"title": "Copy of", "key": "parent", "editable": False, "width": 240},
            {"title": "New File Name", "key": "newFileName", "editable": True, "width": 240},
            {"title": "New Style Name", "key": "newStyleName", "editable": True, "width": 180},
        ]
        self.w.list = List(
            (10, 86, -10, -74),
            self.rows,
            columnDescriptions=columnDescriptions,
            allowsSorting=False,
        )

        self.w.removeButton = Button((10, -40, 150, 24), "Remove Selected", callback=self.removeSelected)
        self.w.createButton = Button((-180, -40, 170, 24), "Create Offspring", callback=self.create)

        addObserver(self, "fontListChanged", "fontDidOpen")
        addObserver(self, "fontListChanged", "fontWillClose")
        self.w.bind("close", self.windowWillClose)

        self.w.open()

    def windowWillClose(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")

    def fontListChanged(self, notification=None):
        currentFont = self.currentParentFont()
        self.fonts = AllFonts()
        self.w.parentPopup.setItems(self.fontLabels())
        if currentFont in self.fonts:
            self.w.parentPopup.set(self.fonts.index(currentFont))

    def fontLabels(self):
        labels = []
        for font in self.fonts:
            path = font.path
            familyName = font.info.familyName or "Untitled"
            styleName = font.info.styleName or ""
            fname = os.path.basename(path) if path else "unsaved"
            labels.append(f"{familyName} {styleName} ({fname})".strip())
        return labels

    def currentParentFont(self):
        i = self.w.parentPopup.get()
        if i is None or i < 0 or i >= len(self.fonts):
            return None
        return self.fonts[i]

    def addRow(self, sender):
        font = self.currentParentFont()
        if font is None:
            return

        path = font.path
        if not path:
            Message("This font has never been saved - save it first.")
            return

        folder = os.path.dirname(path)
        base = os.path.splitext(os.path.basename(path))[0]
        styleName = font.info.styleName or ""
        familyName = font.info.familyName or base

        key = id(font)
        count = self.counters.get(key, 0) + 1
        self.counters[key] = count
        suffix = "" if count == 1 else f"_{count}"

        row = {
            "parent": f"{familyName} ({os.path.basename(path)})",
            "newFileName": f"{base}_copy{suffix}",
            "newStyleName": styleName,
            "_font": font,
            "_folder": folder,
        }
        currentItems = [dict(item) for item in self.w.list]
        currentItems.append(row)
        self.w.list.set(currentItems)

    def removeSelected(self, sender):
        currentItems = [dict(item) for item in self.w.list]
        selection = list(self.w.list.getSelection())
        for i in sorted(selection, reverse=True):
            del currentItems[i]
        self.w.list.set(currentItems)

    def create(self, sender):
        created = 0
        issues = []

        for item in self.w.list:
            folder = item["_folder"]
            font = item["_font"]
            fileName = item["newFileName"].strip()
            styleName = item["newStyleName"].strip()
            label = item["parent"]

            if not fileName:
                issues.append(f"{label}: no file name given")
                continue
            if not fileName.endswith(".ufo"):
                fileName += ".ufo"

            newPath = os.path.join(folder, fileName)
            if os.path.exists(newPath):
                issues.append(f"{fileName}: already exists, skipped")
                continue

            try:
                shutil.copytree(font.path, newPath)
                newFont = OpenFont(newPath, showInterface=True)
                if styleName:
                    newFont.info.styleName = styleName
                newFont.save()
                created += 1
            except Exception as e:
                issues.append(f"{label}: {e}")

        message = f"Created {created} offspring UFO(s)."
        if issues:
            message += "\n\nIssues:\n" + "\n".join(issues)
        Message(message)
