from __future__ import annotations

from typing import Dict

import pandas as pd

COLUMN_ALIASES = {
    "order id": "order_id",
    "orderid": "order_id",
    "order date": "order_date",
    "orderdate": "order_date",
    "customer id": "customer_id",
    "customerid": "customer_id",
    "customer name": "customer_name",
    "customername": "customer_name",
    "product": "product_name",
    "product name": "product_name",
    "productname": "product_name",
    "category": "category",
    "region": "region",
    "quantity": "quantity",
    "qty": "quantity",
    "unit price": "unit_price",
    "unitprice": "unit_price",
    "cost": "cost",
    "revenue": "revenue",
    "profit": "profit",
}

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "product_name",
    "category",
    "region",
    "quantity",
    "unit_price",
]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(column).strip().lower().replace("-", " ").replace("_", " ") for column in normalized.columns]
    normalized = normalized.rename(columns={column: COLUMN_ALIASES.get(column, column.replace(" ", "_")) for column in normalized.columns})
    return normalized


def load_and_prepare_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    sales = _normalize_columns(df)

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in sales.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")
    sales = sales.dropna(subset=["order_date"])

    for numeric_column in ["quantity", "unit_price", "cost", "revenue", "profit"]:
        if numeric_column in sales.columns:
            sales[numeric_column] = pd.to_numeric(sales[numeric_column], errors="coerce")

    sales["quantity"] = sales["quantity"].fillna(0)
    sales["unit_price"] = sales["unit_price"].fillna(0)

    if "revenue" not in sales.columns:
        sales["revenue"] = sales["quantity"] * sales["unit_price"]
    else:
        sales["revenue"] = sales["revenue"].fillna(sales["quantity"] * sales["unit_price"])

    if "cost" not in sales.columns:
        sales["cost"] = sales["revenue"] * 0.7
    else:
        sales["cost"] = sales["cost"].fillna(sales["revenue"] * 0.7)

    if "profit" not in sales.columns:
        sales["profit"] = sales["revenue"] - sales["cost"]
    else:
        sales["profit"] = sales["profit"].fillna(sales["revenue"] - sales["cost"])

    if "customer_name" not in sales.columns:
        sales["customer_name"] = sales["customer_id"].astype(str)

    sales["customer_label"] = sales["customer_name"].fillna(sales["customer_id"].astype(str))
    sales["month"] = sales["order_date"].dt.to_period("M").dt.to_timestamp()
    return sales


def summary_metrics(df: pd.DataFrame) -> Dict[str, float]:
    return {
        "revenue": float(df["revenue"].sum()),
        "profit": float(df["profit"].sum()),
        "orders": int(df["order_id"].nunique()),
        "customers": int(df["customer_id"].nunique()),
        "products": int(df["product_name"].nunique()),
        "avg_order_value": float(df.groupby("order_id")["revenue"].sum().mean()),
    }


def best_selling_products(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("product_name", as_index=False)
        .agg(quantity=("quantity", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
        .sort_values(["revenue", "quantity"], ascending=False)
        .head(top_n)
    )


def top_customers(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return (
        df.groupby(["customer_id", "customer_label"], as_index=False)
        .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"), profit=("profit", "sum"))
        .sort_values(["revenue", "orders"], ascending=False)
        .head(top_n)
    )


def monthly_sales_trends(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("month", as_index=False)
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("month")
    )
    return monthly


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
    )


def profit_analysis(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    analysis = (
        df.groupby("product_name", as_index=False)
        .agg(revenue=("revenue", "sum"), cost=("cost", "sum"), profit=("profit", "sum"))
        .sort_values("profit", ascending=False)
        .head(top_n)
    )
    analysis["margin_pct"] = analysis["profit"] / analysis["revenue"].replace({0: pd.NA}) * 100
    return analysis.fillna(0)


def regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region", as_index=False)
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
    )
