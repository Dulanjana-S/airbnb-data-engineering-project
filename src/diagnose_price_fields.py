from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
SQL_OUTPUTS_DIR = Path("reports/sql_outputs")


def inspect_file(path, columns):
    print("=" * 80)
    print(f"File: {path}")

    if not path.exists():
        print("File not found")
        return

    df = pd.read_csv(path, low_memory=False)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    for column in columns:
        if column in df.columns:
            print(f"\nColumn: {column}")
            print(f"Data type: {df[column].dtype}")
            print("Sample values:")
            print(df[column].dropna().head(10).to_list())
            print(f"Non-null count: {df[column].notna().sum()}")
        else:
            print(f"\nColumn missing: {column}")


def main():
    inspect_file(
        RAW_DIR / "listings.csv.gz",
        ["id", "price", "room_type", "neighbourhood_cleansed"],
    )

    inspect_file(
        PROCESSED_DIR / "clean_listings.csv",
        ["id", "price", "price_clean", "room_type", "neighbourhood_cleansed"],
    )

    inspect_file(
        PROCESSED_DIR / "listing_master.csv",
        ["id", "price", "price_clean", "room_type", "neighbourhood_cleansed"],
    )

    inspect_file(
        SQL_OUTPUTS_DIR / "query_01_output.csv",
        ["room_type", "listing_count", "average_price", "median_price"],
    )


if __name__ == "__main__":
    main()