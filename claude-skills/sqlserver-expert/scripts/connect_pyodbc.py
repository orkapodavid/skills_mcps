#!/usr/bin/env python3
"""
connect_pyodbc.py

Helpers to establish connections to SQL Server using pyodbc.
- Supports SQL Auth, Windows Auth, and DSN connections
- Prints server version and runs a test query
"""
import os
import sys
import pyodbc

DRIVER = os.getenv('SQLSERVER_DRIVER', 'ODBC Driver 18 for SQL Server')
SERVER = os.getenv('SQLSERVER_SERVER', 'localhost')
PORT = os.getenv('SQLSERVER_PORT', '1433')
DATABASE = os.getenv('SQLSERVER_DATABASE', 'master')
UID = os.getenv('SQLSERVER_UID', None)
PWD = os.getenv('SQLSERVER_PWD', None)
TRUSTED = os.getenv('SQLSERVER_TRUSTED', 'false').lower() in ('1','true','yes')
ENCRYPT = os.getenv('SQLSERVER_ENCRYPT', 'yes')
TRUST_CERT = os.getenv('SQLSERVER_TRUST_SERVER_CERT', 'no')
DSN = os.getenv('SQLSERVER_DSN', None)


def make_conn_str():
    if DSN:
        return f'DSN={DSN};DATABASE={DATABASE}'
    base = [
        f'DRIVER={{{{}}}}'.format(DRIVER),
        f'SERVER={SERVER},{PORT}',
        f'DATABASE={DATABASE}',
        f'Encrypt={ENCRYPT}',
        f'TrustServerCertificate={TRUST_CERT}',
    ]
    if TRUSTED:
        base.append('Trusted_Connection=yes')
    else:
        if not UID or not PWD:
            raise RuntimeError('Provide SQLSERVER_UID and SQLSERVER_PWD for SQL Authentication')
        base.extend([f'UID={UID}', f'PWD={PWD}'])
    return ';'.join(base)


def main():
    conn_str = make_conn_str()
    print('Connecting with:', conn_str.replace('PWD='+str(PWD), 'PWD=****'))
    conn = pyodbc.connect(conn_str)
    with conn.cursor() as cur:
        cur.execute('SELECT @@VERSION')
        print('Server version:', cur.fetchone()[0])
        cur.execute('SELECT TOP 1 name FROM sys.databases ORDER BY name')
        print('Sample database:', cur.fetchone()[0])
    conn.close()

if __name__ == '__main__':
    main()
