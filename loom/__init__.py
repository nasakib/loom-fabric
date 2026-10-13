"""Loom Fabric: Heterogeneous Distributed AI Compute Fabric with Ray & Native Model Sharding."""

import subprocess
import sys

__version__ = "0.1.0"
__author__ = "Vector Core Systems"

# Guarantee zero stray console/terminal windows on Windows across GUI, Gateway, and Profiler
if sys.platform == "win32" and not getattr(subprocess.Popen, "_loom_windowless_patched", False):
    _orig_popen_init = subprocess.Popen.__init__

    def _loom_windowless_popen_init(self, *args, **kwargs):
        flags = kwargs.get("creationflags", 0) or 0
        create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        create_new_console = getattr(subprocess, "CREATE_NEW_CONSOLE", 0x00000010)
        if not (flags & create_new_console):
            kwargs["creationflags"] = flags | create_no_window
        _orig_popen_init(self, *args, **kwargs)

    subprocess.Popen.__init__ = _loom_windowless_popen_init  # type: ignore[method-assign]
    subprocess.Popen._loom_windowless_patched = True  # type: ignore[attr-defined]

