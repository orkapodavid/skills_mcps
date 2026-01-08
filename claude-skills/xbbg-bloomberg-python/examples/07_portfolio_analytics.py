"""
07_portfolio_analytics.py
=========================

Purpose:
    Compute portfolio values and daily PnL using BDP

Use Case:
    Simple portfolio dashboard and reporting
"""

from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
from xbbg import blp


@dataclass
class Portfolio:
    positions: Dict[str, float]  # ticker -> shares

    def snapshot(self, fields: List[str] = None) -> pd.DataFrame:
        if fields is None:
            fields = ["PX_LAST", "VOLUME", "DAY_TO_DAY_TOT_RETURN_GROSS_DVDS"]
        df = blp.bdp(list(self.positions.keys()), fields)
        df["Shares"] = [self.positions[t] for t in df.index]
        df["Market_Value"] = df["PX_LAST"] * df["Shares"]
        df["Daily_PnL"] = df["Market_Value"] * df["DAY_TO_DAY_TOT_RETURN_GROSS_DVDS"] / 100.0
        return df


if __name__ == "__main__":
    p = Portfolio({"AAPL US Equity": 1000, "MSFT US Equity": 500})
    print(p.snapshot().head())
