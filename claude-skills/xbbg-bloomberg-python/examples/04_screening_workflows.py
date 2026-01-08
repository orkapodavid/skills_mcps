"""
04_screening_workflows.py
=========================

Purpose:
    Execute BEQS screens and enrich results with BDP/BDS

Use Case:
    Cross-sectional ranking, PIPE candidate discovery
"""

import logging
from xbbg import blp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_screen(screen_name: str):
    screen = blp.beqs(screen=screen_name)  # Requires saved Bloomberg screen
    tickers = screen["ticker"].tolist() if "ticker" in screen.columns else []
    if tickers:
        detail = blp.bdp(tickers, ["CUR_MKT_CAP", "FREE_FLOAT_PCT", "VOLUME_AVG_20D"])
        return screen, detail
    return screen, None


if __name__ == "__main__":
    s, d = run_screen("My Saved Screen")
    print(s.head())
    if d is not None:
        print(d.head())
