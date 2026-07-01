from __future__ import annotations

import pandas as pd
import mysql.connector


def fetch_sales_data_from_mysql(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
) -> pd.DataFrame:
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    try:
        query = f"SELECT * FROM {table}"
        return pd.read_sql(query, connection)
    finally:
        connection.close()
