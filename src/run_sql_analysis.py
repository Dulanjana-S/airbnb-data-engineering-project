from pathlib import Path
import logging

import duckdb
import pandas as pd


DATABASE_PATH = Path("data/database/airbnb_melbourne.duckdb")
SQL_PATH = Path("sql/analysis_queries.sql")
REPORTS_DIR = Path("reports/sql_outputs")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_queries(sql_path):
    sql_text = sql_path.read_text(encoding="utf-8")
    queries = [query.strip() for query in sql_text.split(";") if query.strip()]
    return queries


def create_output_name(query_number):
    return REPORTS_DIR / f"query_{query_number:02d}_output.csv"


def run_analysis_queries():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}")

    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_PATH}")

    queries = load_queries(SQL_PATH)

    connection = duckdb.connect(str(DATABASE_PATH))

    for index, query in enumerate(queries, start=1):
        logging.info("Running SQL query %s", index)

        result_df = connection.execute(query).fetchdf()
        output_path = create_output_name(index)

        result_df.to_csv(output_path, index=False)
        logging.info("Saved query output to %s", output_path)

    connection.close()


def main():
    run_analysis_queries()


if __name__ == "__main__":
    main()