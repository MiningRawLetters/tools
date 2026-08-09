# MRL Diacritic Width Check - Main Entry Point
# Developed by Kevin Kuhn (Mining Raw Letters)

import sys
import importlib

# RoboFont keeps this extension's modules in sys.modules for the whole app
# session. Without forcing a reload, reinstalling the .roboFontExt after an
# edit updates the files on disk but the already-open RoboFont keeps running
# the stale, previously-imported code until the app is quit and relaunched.
for _mod_name in ("mrl_diacritic_width_check_utils", "mrl_diacritic_width_check_controller"):
    if _mod_name in sys.modules:
        importlib.reload(sys.modules[_mod_name])

from mrl_diacritic_width_check_controller import MRL_DiacriticWidthCheckController

MRL_DiacriticWidthCheckController()
