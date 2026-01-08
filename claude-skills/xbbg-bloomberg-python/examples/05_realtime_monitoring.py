"""
05_realtime_monitoring.py
=========================

Purpose:
    Subscribe to real-time updates for a list of tickers

Use Case:
    Lightweight market monitors and alerts
"""

import logging
from typing import List
from xbbg import blp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def subscribe_prices(tickers: List[str], fields: List[str] = None, interval: int = 10):
    if fields is None:
        fields = ["LAST_PRICE", "VOLUME"]
    # NOTE: Actual streaming requires an event loop/callback in your environment
    # The following illustrates the subscription call signature
    return blp.subscribe(tickers, fields, interval=interval)  # doctest: +SKIP


if __name__ == "__main__":
    # Example usage (will not print without callback / context)
    subscribe_prices(["AAPL US Equity", "MSFT US Equity"])  # doctest: +SKIP
