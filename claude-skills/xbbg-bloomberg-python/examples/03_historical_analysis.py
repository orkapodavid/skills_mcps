"""
03_historical_analysis.py
=========================

Purpose:
    Quarterly fundamentals and price trends using bdh()

Use Case:
    Backtesting, cross-sectional factor analysis, trend detection
"""

import logging
import pandas as pd
from xbbg import blp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def fundamentals_quarterly(tickers):
    flds = [
        "SALES_REV_TURN", "OPER_INC", "NET_INCOME", "EBITDA", "FREE_CASH_FLOW", "RETURN_ON_EQUITY"
    ]
    df = blp.bdh(tickers, flds, start_date="2019-01-01", Per="QUARTERLY")
    # Example derived metrics (requires post-processing to align levels)
    return df


def price_trends(tickers):
    df = blp.bdh(tickers, ["PX_LAST"], start_date="2024-01-01")
    returns = df.groupby(level=1)["PX_LAST"].pct_change()
    rolling_vol = returns.groupby(level=1).rolling(window=20).std().droplevel(0) * (252 ** 0.5)
    return returns, rolling_vol


if __name__ == "__main__":
    tickers = ["AAPL US Equity", "MSFT US Equity"]
    fund = fundamentals_quarterly(tickers)
    print(fund.head())
    r, vol = price_trends(tickers)
    print(r.head())
    print(vol.head())
