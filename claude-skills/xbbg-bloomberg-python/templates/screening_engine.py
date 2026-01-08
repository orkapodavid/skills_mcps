"""
screening_engine.py
===================
Investment screening framework using BEQS + BDP/BDS.
"""

from typing import List, Tuple, Optional
import pandas as pd
from xbbg import blp


def run_beqs(screen: str) -> pd.DataFrame:
    return blp.beqs(screen=screen)


def enrich_bdp(tickers: List[str]) -> pd.DataFrame:
    return blp.bdp(tickers, ["CUR_MKT_CAP", "FREE_FLOAT_PCT", "VOLUME_AVG_20D", "PE_RATIO", "VOLATILITY_30D"])


def pipeline(screen: str) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    res = run_beqs(screen)
    tickers = res["ticker"].tolist() if "ticker" in res.columns else []
    detail = enrich_bdp(tickers) if tickers else None
    return res, detail
