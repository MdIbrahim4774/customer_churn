import os
import shutil
import pandas as pd
from sqlalchemy import create_engine, text

LANDING_DIR = "data/landing"
RAW_DIR = "data/raw"
REJECTED_DIR = "data/rejected"
LOG_DIR = "data/logs"

EXPECTED_COLS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]

DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)


def detect_files():
    files = []

    for filename in os.listdir(LANDING_DIR):
        if filename.lower().endswith(".csv"):
            files.append(os.path.join(LANDING_DIR, filename))

    return files


def validate_schema(filepath):
    df = pd.read_csv(filepath, nrows=0)

    return list(df.columns) == EXPECTED_COLS


def load_to_staging(filepath, engine):
    df = pd.read_csv(filepath)

    df.to_sql(
        "stg_customer_raw",
        con=engine,
        if_exists="append",
        index=False
    )

    return len(df)


def log_ingestion(filename, status, rows):
    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO ingestion_log
                (filename, row_count, load_timestamp, status)
                VALUES
                (:filename, :row_count, NOW(), :status)
            """),
            {
                "filename": filename,
                "row_count": rows,
                "status": status
            }
        )


def process_landing():
    files = detect_files()

    for filepath in files:
        filename = os.path.basename(filepath)

        if validate_schema(filepath):
            try:
                rows = load_to_staging(filepath, engine)

                log_ingestion(
                    filename,
                    "LOADED",
                    rows
                )

                shutil.move(
                    filepath,
                    os.path.join(RAW_DIR, filename)
                )

            except Exception:
                log_ingestion(
                    filename,
                    "REJECTED",
                    0
                )

                shutil.move(
                    filepath,
                    os.path.join(REJECTED_DIR, filename)
                )

        else:
            log_ingestion(
                filename,
                "REJECTED",
                0
            )

            shutil.move(
                filepath,
                os.path.join(REJECTED_DIR, filename)
            )

if __name__ == "__main__":
    process_landing()