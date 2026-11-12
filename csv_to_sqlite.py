"""Load project CSV files into the local SQLite database."""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "workmind.db"


TABLES = {
    "customer_purchase_history": {
        "csv_path": PROJECT_ROOT / "customer_purchase_history.csv",
        "columns": [
            ("order_number", "TEXT"),
            ("customer_id", "TEXT"),
            ("name", "TEXT"),
            ("address", "TEXT"),
            ("city", "TEXT"),
            ("country", "TEXT"),
            ("continent", "TEXT"),
            ("purchase_date", "TEXT"),
            ("payment_method", "TEXT"),
            ("product", "TEXT"),
            ("product_category", "TEXT"),
            ("quantity", "INTEGER"),
            ("product_id", "TEXT"),
            ("product_price", "REAL"),
            ("cost_price", "REAL"),
            ("discount_percentage", "REAL"),
            ("discounted_price", "REAL"),
            ("final_price", "REAL"),
            ("profit", "REAL"),
            ("warranty_period", "TEXT"),
        ],
        "source_columns": [
            "OrderNumber",
            "CustomerID",
            "Name",
            "Address",
            "City",
            "Country",
            "Continent",
            "PurchaseDate",
            "PaymentMethod",
            "Product",
            "ProductCategory",
            "Quantity",
            "ProductID",
            "ProductPrice",
            "CostPrice",
            "DiscountPercentage",
            "DiscountedPrice",
            "FinalPrice",
            "Profit",
            "WarrantyPeriod",
        ],
        "integer_columns": {"quantity"},
        "real_columns": {
            "product_price",
            "cost_price",
            "discount_percentage",
            "discounted_price",
            "final_price",
            "profit",
        },
        "date_columns": {"purchase_date": "%m/%d/%Y"},
    },
}


def clean_value(value: str | None) -> str | None:
    """Convert blank CSV values to None while preserving literal values like N/A."""
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def normalize_date(value: str, source_format: str) -> str | None:
    """Normalize a CSV date value to YYYY-MM-DD text."""
    value = clean_value(value)
    if value is None:
        return None
    return datetime.strptime(value, source_format).date().isoformat()


def convert_value(value: str, column_name: str, table_config: dict):
    """Convert CSV strings to the configured SQLite-friendly value."""
    value = clean_value(value)
    if value is None:
        return None

    if column_name in table_config["integer_columns"]:
        return int(value)

    if column_name in table_config.get("real_columns", set()):
        return float(value)

    if column_name in table_config["date_columns"]:
        return normalize_date(value, table_config["date_columns"][column_name])

    return value


def create_table(connection: sqlite3.Connection, table_name: str, columns: list) -> None:
    """Replace a SQLite table with the configured schema."""
    connection.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    column_sql = ", ".join(f'"{name}" {column_type}' for name, column_type in columns)
    connection.execute(f'CREATE TABLE "{table_name}" ({column_sql})')


def load_table(connection: sqlite3.Connection, table_name: str, table_config: dict) -> int:
    """Load one CSV file into its SQLite table."""
    columns = [name for name, _ in table_config["columns"]]
    source_columns = table_config["source_columns"]
    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(f'"{col}"' for col in columns)
    insert_sql = f'INSERT INTO "{table_name}" ({quoted_columns}) VALUES ({placeholders})'

    create_table(connection, table_name, table_config["columns"])

    row_count = 0
    with table_config["csv_path"].open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            values = [
                convert_value(row[src_col], col_name, table_config)
                for src_col, col_name in zip(source_columns, columns)
            ]
            connection.execute(insert_sql, values)
            row_count += 1

    return row_count


def main() -> None:
    """Create the local database and load all configured CSV tables."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        loaded_counts = {
            table_name: load_table(connection, table_name, table_config)
            for table_name, table_config in TABLES.items()
        }
        connection.commit()

    print(f"SQLite database updated: {DB_PATH}")
    for table_name, row_count in loaded_counts.items():
        print(f"  - {table_name}: {row_count:,} rows loaded")


if __name__ == "__main__":
    main()
