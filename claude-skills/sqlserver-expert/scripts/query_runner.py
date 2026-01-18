#!/usr/bin/env python3
"""
query_runner.py

Execute parameterized queries safely with timing and simple retry.
"""
import time
import pyodbc
import os

DRIVER = os.getenv('SQLSERVER_DRIVER', 'ODBC Driver 18 for SQL Server')
SERVER = os.getenv('SQLSERVER_SERVER', 'localhost')
PORT = os.getenv('SQLSERVER_PORT', '1433')
DATABASE = os.getenv('SQLSERVER_DATABASE', 'master')
UID = os.getenv('SQLSERVER_UID', None)
PWD = os.getenv('SQLSERVER_PWD', None)
ENCRYPT = os.getenv('SQLSERVER_ENCRYPT', 'yes')
TRUST_CERT = os.getenv('SQLSERVER_TRUST_SERVER_CERT', 'no')

CONN_STR = ';'.join([
    f'DRIVER={{{{}}}}'.format(DRIVER),
    f'SERVER={SERVER},{PORT}',
    f'DATABASE={DATABASE}',
    f'UID={UID}',
    f'PWD={PWD}',
    f'Encrypt={ENCRYPT}',
    f'TrustServerCertificate={TRUST_CERT}',
])

TRANSIENT_ERROR_CODES = {1205, 4060, 10928, 10929}


def run_query(sql, params=None, retries=3):
    params = params or ()
    attempt = 0
    while True:
        try:
            with pyodbc.connect(CONN_STR) as conn:
                start = time.time()
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    if cur.description:
                        rows = cur.fetchall()
                    else:
                        rows = []
                        conn.commit()
                elapsed = (time.time() - start) * 1000
                print(f'Elapsed: {elapsed:.1f} ms, rows: {len(rows)}')
                return rows
        except pyodbc.Error as e:
            attempt += 1
            code = getattr(e, 'args', [None, None])[0]
            print('Error:', e)
            if attempt <= retries and (isinstance(code, int) and code in TRANSIENT_ERROR_CODES):
                sleep = 0.5 * attempt
                print(f'Transient error; retrying in {sleep}s (attempt {attempt}/{retries})')
                time.sleep(sleep)
                continue
            raise


if __name__ == '__main__':
    rows = run_query('SELECT name FROM sys.databases WHERE database_id < ?', (10,))
    for r in rows:
        print(r[0])
