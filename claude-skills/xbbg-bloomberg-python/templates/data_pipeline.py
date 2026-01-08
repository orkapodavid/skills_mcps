"""
data_pipeline.py
================
Reusable ETL patterns for xbbg data pipelines.
"""

from typing import List, Callable
import pandas as pd
from xbbg import blp


def batch_process(tickers: List[str], op: Callable[[List[str]], pd.DataFrame], batch_size: int = 50) -> pd.DataFrame:
    """Process large lists of tickers in batches and concatenate results."""
    out = []
    for i in range(0, len(tickers), batch_size):
        out.append(op(tickers[i : i + batch_size]))
    return pd.concat(out)


def price_history(tickers: List[str], fields: List[str], start_date: str) -> pd.DataFrame:
    return blp.bdh(tickers, fields, start_date=start_date, Fill="P", Days="T")
