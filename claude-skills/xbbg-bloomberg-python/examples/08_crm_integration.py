"""
08_crm_integration.py
=====================

Purpose:
    Pattern for enriching Microsoft Dynamics 365 with xbbg data

Use Case:
    PIPE opportunity enrichment and sales analytics
"""

import logging
from datetime import datetime
from typing import Dict

import requests
from xbbg import blp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def enrich_dynamics_opportunity(dynamics_url: str, access_token: str, opportunity_id: str, ticker: str) -> bool:
    market = blp.bdp(ticker, ["PX_LAST", "CUR_MKT_CAP", "FREE_FLOAT_PCT", "VOLUME_AVG_20D", "VOLATILITY_30D", "PE_RATIO"]).iloc[0]
    holders = blp.bds(ticker, "TOP_20_HOLDERS_PUBLIC_FILINGS")
    top = holders.iloc[0] if not holders.empty else None

    data: Dict = {
        "customfield_currentprice": float(market["PX_LAST"]),
        "customfield_marketcap": float(market["CUR_MKT_CAP"]),
        "customfield_freefloat": float(market["FREE_FLOAT_PCT"]),
        "customfield_liquidity": float(market["VOLUME_AVG_20D"]),
        "customfield_volatility": float(market["VOLATILITY_30D"]),
        "customfield_peratio": float(market["PE_RATIO"]),
        "customfield_topshareholder": top["Holder Name"] if top is not None else None,
        "customfield_topholdershipct": top["Portfolio Pct"] if top is not None else None,
        "customfield_lastupdate": datetime.now().isoformat(),
    }

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    resp = requests.patch(f"{dynamics_url}/api/data/v9.2/opportunities({opportunity_id})", headers=headers, json=data)
    return resp.status_code == 204


if __name__ == "__main__":
    print("Integration function ready (requires valid Dynamics endpoint & token)")
