import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

DB_URL = "mysql+pymysql://root:root@localhost/customer_churn"

CSV_PATH = "data/raw/Telco-Customer-Churn.csv"

engine = create_engine(DB_URL)

def process_incremental(csv_path, engine):
    df = pd.read_csv(csv_path)

    df.columns = [
        column.strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    df["senior_citizen"] = df["seniorcitizen"].astype(int)

    df["partner"] = df["partner"].map({
        "Yes": 1,
        "No": 0
    })

    df["dependents"] = df["dependents"].map({
        "Yes": 1,
        "No": 0
    })

    existing = pd.read_sql(
        """
        SELECT
            customer_id,
            gender,
            senior_citizen,
            partner,
            dependents,
            internet_service
        FROM customers
        """,
        engine
    )

    existing = existing.set_index("customer_id")

    rows_inserted = 0
    rows_updated = 0
    rows_unchanged = 0

    upsert_sql = text("""
        INSERT INTO customers (
            customer_id,
            gender,
            senior_citizen,
            partner,
            dependents,
            internet_service
        )
        VALUES (
            :customer_id,
            :gender,
            :senior_citizen,
            :partner,
            :dependents,
            :internet_service
        )
        ON DUPLICATE KEY UPDATE
            gender = VALUES(gender),
            senior_citizen = VALUES(senior_citizen),
            partner = VALUES(partner),
            dependents = VALUES(dependents),
            internet_service = VALUES(internet_service)
    """)

    columns = [
        "gender",
        "senior_citizen",
        "partner",
        "dependents",
        "internet_service"
    ]

    with engine.begin() as connection:
        for _, row in df.iterrows():

            customer_id = row["customerid"]

            new_values = {
                "customer_id": customer_id,
                "gender": row["gender"],
                "senior_citizen": row["senior_citizen"],
                "partner": row["partner"],
                "dependents": row["dependents"],
                "internet_service": row["internetservice"]
            }

            if customer_id not in existing.index:
                connection.execute(upsert_sql, new_values)
                rows_inserted += 1
                continue

            old_values = existing.loc[customer_id]

            changed = any(
                old_values[column] != new_values[column]
                for column in columns
            )

            if changed:
                connection.execute(upsert_sql, new_values)
                rows_updated += 1
            else:
                rows_unchanged += 1

    
    run_timestamp = datetime.now()
    with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO pipeline_run_log (
                        file_name,
                        rows_inserted,
                        rows_updated,
                        rows_unchanged,
                        run_timestamp
                    )
                    VALUES (
                        :file_name,
                        :rows_inserted,
                        :rows_updated,
                        :rows_unchanged,
                        :run_timestamp
                    )
                """),
                {
                    "file_name": csv_path,
                    "rows_inserted": rows_inserted,
                    "rows_updated": rows_updated,
                    "rows_unchanged": rows_unchanged,
                    "run_timestamp": run_timestamp
                }
            )

    print("Pipeline Run")
    print(f"Rows inserted: {rows_inserted}")
    print(f"Rows updated: {rows_updated}")
    print(f"Rows unchanged: {rows_unchanged}")
    print(f"Run timestamp: {run_timestamp}")

    return rows_inserted, rows_updated, rows_unchanged

process_incremental(CSV_PATH, engine)