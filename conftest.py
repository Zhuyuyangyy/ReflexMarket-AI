"""Root conftest.py - ensures all paths are set up before test collection."""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

for p in [PROJECT_ROOT, BACKEND_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)
