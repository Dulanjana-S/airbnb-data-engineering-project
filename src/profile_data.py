from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

files = {
    "listings": "listings.csv.gz",
    "calendar": "calendar.csv.gz",
    "reviews": "reviews.csv.gz",
    "neighbourhoods": "neighbourhoods.csv",
}

profile_rows = []

print("\nStarting data profiling...\n")

for dataset_name, filename in files.items():
    file_path = RAW_DIR / filename

    print("=" * 80)
    print(f"Profiling: {filename}")

    if not file_path.exists():
        print(f"Missing file: {filename}")
        continue

    df = pd.read_csv(file_path, low_memory=False)

    row_count = len(df)
    column_count = len(df.columns)

    print(f"Rows: {row_count}")
    print(f"Columns: {column_count}")

    for column in df.columns:
        null_count = df[column].isna().sum()
        null_percentage = round((null_count / row_count) * 100, 2) if row_count > 0 else 0
        unique_count = df[column].nunique(dropna=True)

        sample_values = (
            df[column]
            .dropna()
            .astype(str)
            .head(3)
            .tolist()
        )

        profile_rows.append({
            "dataset": dataset_name,
            "filename": filename,
            "row_count": row_count,
            "column_count": column_count,
            "column_name": column,
            "data_type": str(df[column].dtype),
            "null_count": null_count,
            "null_percentage": null_percentage,
            "unique_count": unique_count,
            "sample_values": " | ".join(sample_values)
        })

profile_df = pd.DataFrame(profile_rows)

output_path = REPORTS_DIR / "data_quality_report.csv"
profile_df.to_csv(output_path, index=False)

print("\nData profiling completed.")
print(f"Report saved to: {output_path}")
