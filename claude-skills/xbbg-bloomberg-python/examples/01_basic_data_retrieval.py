"""
01_basic_data_retrieval.py
==========================

Purpose:
    Demonstrates xbbg reference (bdp) and historical (bdh) data retrieval

Use Case:
    Quick data pulls for research notebooks and scripts

Prerequisites:
    - Bloomberg Terminal running and logged in
    - xbbg installed: pip install xbbg
    - Python 3.10+

Expected Runtime:
    <5 seconds for small requests
"""

import logging
from typing import List, Optional

import pandas as pd
from xbbg import blp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_reference(tickers: List[str], fields: List[str], **kwargs) -> pd.DataFrame:
    """
    Fetch point-in-time reference data

    Args:
        tickers: List of Bloomberg identifiers
        fields: Field mnemonics (use uppercase)
        kwargs: Optional connection overrides (e.g., server, port)

    Returns:
        DataFrame with rows=tickers, columns=fields
    """
    logger.info("Fetching reference data: %d tickers, %d fields", len(tickers), len(fields))
    return blp.bdp(tickers=tickers, flds=fields, **kwargs)


def get_history(tickers: List[str], fields: List[str], start_date: str, end_date: Optional[str] = None, **kwargs) -> pd.DataFrame:
    """
    Fetch historical end-of-day time series

    Args:
        tickers: List of Bloomberg identifiers
        fields: Field mnemonics
        start_date: Start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        kwargs: Overrides like Per, Fill, Days, currency

    Returns:
        DataFrame with MultiIndex (date, ticker)
    """
    logger.info("Fetching historical data: %d tickers, fields=%s, start=%s, end=%s", len(tickers), fields, start_date, end_date)
    return blp.bdh(tickers=tickers, flds=fields, start_date=start_date, end_date=end_date, **kwargs)


if __name__ == "__main__":
    tickers = ["AAPL US Equity", "MSFT US Equity"]
    fields = ["PX_LAST", "VOLUME"]

    ref = get_reference(tickers, fields)
    print("\nReference sample:\n", ref.head())

    hist = get_history(tickers, fields, start_date="2025-12-01")
    print("\nHistory sample:\n", hist.head())
