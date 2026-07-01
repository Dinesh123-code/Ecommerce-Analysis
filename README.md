# E-Commerce Sales Analysis Dashboard

A Streamlit dashboard for analyzing e-commerce sales data stored in MySQL or uploaded as CSV.

## What it shows

- Best-selling products
- Top customers
- Monthly sales trends
- Revenue by category
- Profit analysis
- Regional performance

## Project Flow

CSV Dataset -> MySQL -> Python (Pandas) -> Analysis -> Charts -> Streamlit Dashboard

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure MySQL settings:

Copy `.env.example` to `.env` and update the values.

3. Create the database schema:

Run `sql/schema.sql` in MySQL.

4. Load your CSV data into MySQL:

```bash
python scripts/load_csv_to_mysql.py path\to\sales.csv --host localhost --port 3306 --user root --password your_password --database ecommerce_db
```

5. Launch the dashboard:

```bash
streamlit run app.py
```

## Expected CSV Columns

The app expects columns similar to:

- `order_id`
- `order_date`
- `customer_id`
- `customer_name`
- `product_name`
- `category`
- `region`
- `quantity`
- `unit_price`
- `cost`
- `revenue`
- `profit`

Missing `revenue` and `profit` values are calculated when possible.
