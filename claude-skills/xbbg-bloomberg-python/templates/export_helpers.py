"""
export_helpers.py
=================
Helpers for exporting data (CSV, Excel, JSON, SQL placeholder).
"""

import pandas as pd
from sqlalchemy import create_engine


def to_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=True)


def to_excel(df: pd.DataFrame, path: str, sheet_name: str = "Sheet1") -> None:
    with pd.ExcelWriter(path) as xw:
        df.to_excel(xw, sheet_name=sheet_name)


def to_sql(df: pd.DataFrame, url: str, table: str) -> None:
    engine = create_engine(url)
    df.to_sql(table, engine, if_exists="append", index=True, method="multi")
