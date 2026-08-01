"""Locate and import the ExaDiS python binding of this OpenDiS checkout."""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYEXADIS_PATHS = [
    os.path.join(REPO_ROOT, "python"),
    os.path.join(REPO_ROOT, "lib"),
    os.path.join(REPO_ROOT, "core", "pydis", "python"),
    os.path.join(REPO_ROOT, "core", "exadis", "python"),
]


def setup_paths() -> None:
    for path in PYEXADIS_PATHS:
        if os.path.isdir(path) and path not in sys.path:
            sys.path.append(path)


def import_pyexadis():
    """Import and return the ``pyexadis`` module, raising a helpful error."""
    setup_paths()
    try:
        import pyexadis  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depends on the build
        raise ImportError(
            "Cannot import pyexadis. Build OpenDiS with the ExaDiS python binding:\n"
            "  ./configure.sh -DCMAKE_BUILD_TYPE=Release -DEXADIS_PYTHON_BINDING=On\n"
            "  cmake --build build -j 8 && cmake --build build --target install"
        ) from exc
    return pyexadis


_INITIALIZED = False


def initialize():
    """Initialize the ExaDiS/Kokkos runtime once per process.

    Kokkos can only be initialized once per process, so the runtime is left
    alive for the lifetime of the process and finalized at exit.  This lets a
    single process generate, run and post-process several cases in a row.
    """
    global _INITIALIZED
    pyexadis = import_pyexadis()
    if not _INITIALIZED:
        import atexit

        pyexadis.initialize()
        _INITIALIZED = True
        atexit.register(finalize)
    return pyexadis


def finalize() -> None:
    """Finalize the ExaDiS/Kokkos runtime (called automatically at exit)."""
    global _INITIALIZED
    if _INITIALIZED:
        import pyexadis

        pyexadis.finalize()
        _INITIALIZED = False
