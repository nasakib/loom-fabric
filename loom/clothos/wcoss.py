# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
WCOSS alias for WCOS (Windows ClothOS Subsystem).
Module: `loom/clothos/wcoss.py` -> Delegates directly to `loom.clothos.wcos`.
"""

from __future__ import annotations

import sys
from loom.clothos.wcos import WCOS, main

WCOSS = WCOS

if __name__ == "__main__":
    sys.exit(main())
