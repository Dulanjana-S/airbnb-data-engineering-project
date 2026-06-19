from pathlib import Path
import logging
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PIPELINE_STEPS = [
    "src/check_data.py",
    "src/profile_data.py",
    "src/clean_data.py",
    "src/build_master_table.py",
    "src/build_database.py",
    "src/run_sql_analysis.py",
    "src/create_eda_outputs.py",
    "src/create_statistical_analysis.py",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_script(script_path):
    full_path = PROJECT_ROOT / script_path

    if not full_path.exists():
        raise FileNotFoundError(f"Pipeline script not found: {full_path}")

    logging.info("Running pipeline component: %s", script_path)

    subprocess.run(
        [sys.executable, str(full_path)],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main():
    logging.info("Starting Airbnb data engineering pipeline")

    for script_path in PIPELINE_STEPS:
        run_script(script_path)

    logging.info("Airbnb data engineering pipeline completed successfully")


if __name__ == "__main__":
    main()