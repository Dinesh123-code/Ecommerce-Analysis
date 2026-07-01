from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import mysql.connector
from mysql.connector import Error

from src.analytics import load_and_prepare_sales_data

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ecommerce_sales (
    order_id VARCHAR(64) NOT NULL,
    order_date DATE NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    customer_name VARCHAR(255),
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 0,
    unit_price DECIMAL(12, 2) DEFAULT 0,
    cost DECIMAL(12, 2) DEFAULT 0,
    revenue DECIMAL(12, 2) DEFAULT 0,
    profit DECIMAL(12, 2) DEFAULT 0
);
"""

INSERT_SQL = """
INSERT INTO ecommerce_sales (
    order_id, order_date, customer_id, customer_name, product_name,
    category, region, quantity, unit_price, cost, revenue, profit
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def ensure_table(connection: mysql.connector.MySQLConnection) -> None:
    cursor = connection.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    connection.commit()
    cursor.close()


def import_csv_to_mysql(csv_path: Path, host: str, port: int, user: str, password: str, database: str) -> None:
    raw_df = pd.read_csv(csv_path)
    sales_df = load_and_prepare_sales_data(raw_df)

    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    try:
        ensure_table(connection)
        cursor = connection.cursor()
        rows = []
        for _, row in sales_df.iterrows():
            rows.append(
                (
                    str(row["order_id"]),
                    row["order_date"].date(),
                    str(row["customer_id"]),
                    None if pd.isna(row.get("customer_name")) else str(row.get("customer_name")),
                    str(row["product_name"]),
                    str(row["category"]),
                    str(row["region"]),
                    int(row["quantity"]),
                    float(row["unit_price"]),
                    float(row["cost"]),
                    float(row["revenue"]),
                    float(row["profit"]),
                )
            )
        cursor.executemany(INSERT_SQL, rows)
        connection.commit()
        cursor.close()
        print(f"Imported {len(rows)} rows into ecommerce_sales")
    finally:
        connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load a CSV dataset into MySQL for the dashboard.")
    parser.add_argument("csv_path", type=Path, help="Path to the CSV file")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=3306)
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="")
    parser.add_argument("--database", default="ecommerce_db")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        import_csv_to_mysql(args.csv_path, args.host, args.port, args.user, args.password, args.database)
    except Error as exc:
        raise SystemExit(f"MySQL import failed: {exc}") from exc
