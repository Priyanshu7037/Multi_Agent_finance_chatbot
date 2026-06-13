from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

from tools.nse_universe import group_by_sector


@lru_cache(maxsize=4)
def build_stock_universe() -> Dict[str, List[str]]:
    return group_by_sector()
