"""
02_bulk_data_operations.py
==========================

Purpose:
    Demonstrates bulk/tabular queries via bds (dividends, shareholders)

Use Case:
    Ownership analysis, dividend history, earnings announcements

Prerequisites:
    - Bloomberg Terminal running and logged in
    - xbbg installed: pip install xbbg

Expected Runtime:
    5–15 seconds depending on field
"""

import logging
from typing import List

import pandas as pd
from xbbg import blp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def top_shareholders(ticker: str) -> pd.DataFrame:
    """Top 20 holders from public filings"""
    df = blp.bds(tickers=ticker, flds="TOP_20_HOLDERS_PUBLIC_FILINGS")
    return df


def dividends_history(tickers: List[str]) -> pd.DataFrame:
    """Dividend history for one or more tickers"""
    dfs = [blp.bds(t, "DVD_HIST_ALL") for t in tickers]
    return pd.concat(dfs, ignore_index=False)


if __name__ == "__main__":
    print(top_shareholders("AAPL US Equity").head())
    print(dividends_history(["AAPL US Equity", "MSFT US Equity"]).head())
