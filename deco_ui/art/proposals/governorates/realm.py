"""The governorates' data for the mockups in this folder: moved to scripts/rouental_realm.py (2026-10-21, night), where
the game's governorates window reads it too (scripts/rouental_ui.py)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..",
                                                "scripts")))
from rouental_realm import *  # noqa: E402,F401,F403
from rouental_realm import _edges, _runs  # noqa: E402,F401
