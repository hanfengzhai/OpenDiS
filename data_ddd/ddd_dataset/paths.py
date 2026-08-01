"""Make the OpenDiS python packages (framework, pydis, pydis_lib) importable.

The repository layout places the framework package under python/, the pydis
core under core/pydis/python/ and the compiled ctypes bindings under lib/.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_PYDIS_PATHS = [
    os.path.join(REPO_ROOT, "python"),
    os.path.join(REPO_ROOT, "lib"),
    os.path.join(REPO_ROOT, "core", "pydis", "python"),
]

for _p in _PYDIS_PATHS:
    if _p not in sys.path:
        sys.path.append(_p)
