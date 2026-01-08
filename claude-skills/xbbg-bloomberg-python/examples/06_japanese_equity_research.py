"""
06_japanese_equity_research.py
==============================

Purpose:
    TSE-specific workflows: session filtering and ticker formats

Use Case:
    Japan equity analytics and intraday research
"""

import logging
from xbbg import blp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def tse_intraday_example():
    # 7974 JT Equity = Nintendo Co Ltd
    df = blp.bdib(ticker="7974 JT Equity", dt="2025-12-01", session="am_open_30")
    return df.tail()


if __name__ == "__main__":
    print(tse_intraday_example())
