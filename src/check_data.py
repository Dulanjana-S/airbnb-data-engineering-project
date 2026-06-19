from pathlib import Path
import pandas as pd
import json

RAW_DIR = Path("data/raw")

files = {
    "listings": "listings.csv.gz",
    "calendar": "calendar.csv.gz",
    "reviews": "reviews.csv.gz",
    "neighbourhoods": "neighbourhoods.csv",
    "neighbourhoods_geojson": "neighbourhoods.geojson",
}

print("\nChecking raw data files...\n")

for name, filename in files.items():
    file_path = RAW_DIR / filename

    print("=" * 80)
    print(f"File: {filename}")

    if not file_path.exists():
        print("Status: MISSING")
        continue

    print("Status: FOUND")

    if filename.endswith(".csv") or filename.endswith(".csv.gz"):
        df = pd.read_csv(file_path, nrows=5)
        print(f"Sample rows loaded: {len(df)}")
        print(f"Columns found: {len(df.columns)}")
        print("\nColumn names:")
        for col in df.columns:
            print(f"- {col}")

        print("\nSample data:")
        print(df.head())

    elif filename.endswith(".geojson"):
        with open(file_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        print("GeoJSON loaded successfully")
        print(f"GeoJSON type: {geojson_data.get('type')}")
        print(f"Number of features: {len(geojson_data.get('features', []))}")

