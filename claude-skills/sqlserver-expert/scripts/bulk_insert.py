#!/usr/bin/env python3
"""
bulk_insert.py

Fast bulk insert using pyodbc fast_executemany from CSV.
"""
import csv
import os
import pyodbc

DRIVER = os.getenv('SQLSERVER_DRIVER', 'ODBC Driver 18 for SQL Server')
SERVER = os.getenv('SQLSERVER_SERVER', 'localhost')
PORT = os.getenv('SQLSERVER_PORT', '1433')
DATABASE = os.getenv('SQLSERVER_DATABASE', 'master')
UID = os.getenv('SQLSERVER_UID', None)
PWD = os.getenv('SQLSERVER_PWD', None)
ENCRYPT = os.getenv('SQLSERVER_ENCRYPT', 'yes')
TRUST_CERT = os.getenv('SQLSERVER_TRUST_SERVER_CERT', 'no')
TABLE = os.getenv('SQLSERVER_TABLE', 'dbo.Target')
CSV_PATH = os.getenv('CSV_PATH', 'data.csv')

CONN_STR = ';'.join([
    f'DRIVER={{{{}}}}'.format(DRIVER),
    f'SERVER={SERVER},{PORT}',
    f'DATABASE={DATABASE}',
    f'UID={UID}',
    f'PWD={PWD}',
    f'Encrypt={ENCRYPT}',
    f'TrustServerCertificate={TRUST_CERT}',
])


def load_csv_rows(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [tuple(r) for r in reader]
    return header, rows


def main():
    header, rows = load_csv_rows(CSV_PATH)
    placeholders = ','.join(['?'] * len(header))
    sql = f'INSERT INTO {TABLE} ({",".join(header)}) VALUES ({placeholders})'
    with pyodbc.connect(CONN_STR) as conn:
        cur = conn.cursor()
        cur.fast_executemany = True
        cur.executemany(sql, rows)
        conn.commit()
        print(f'Inserted {len(rows)} rows into {TABLE}')

if __name__ == '__main__':
    main()
