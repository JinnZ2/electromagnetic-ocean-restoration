"""Shared pytest configuration.

The physics modules live in ``equations/`` and import each other by bare
module name (``from wave_energy import ...``), so that directory has to be
on ``sys.path`` before the test modules import anything.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EQUATIONS_DIR = os.path.join(REPO_ROOT, "equations")
TOOLS_DIR = os.path.join(REPO_ROOT, "community-tools")

for path in (EQUATIONS_DIR, TOOLS_DIR, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)
