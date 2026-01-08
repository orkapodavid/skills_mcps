"""
portfolio_monitor.py
====================
Utilities for position tracking and simple reporting.
"""

from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
from xbbg import blp


@dataclass
class PortfolioMonitor:
    holdings: Dict[str, float]  # ticker -> shares

    def snapshot(self, fields: List[str] = None) -> pd.DataFrame:
        if fields is None:
            fields = ["PX_LAST", "DAY_TO_DAY_TOT_RETURN_GROSS_DVDS", "VOLUME"]
        df = blp.bdp(list(self.holdings.keys()), fields)
        df["Shares"] = [self.holdings[t] for t in df.index]
        df["Market_Value"] = df["PX_LAST"] * df["Shares"]
        df["Daily_PnL"] = df["Market_Value"] * df["DAY_TO_DAY_TOT_RETURN_GROSS_DVDS"] / 100.0
        return df
