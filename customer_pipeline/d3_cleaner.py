import pandas as pd
from sqlalchemy import create_engine, text
from customer_cleaner import CustomerCleaner

DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)


def clean_staging(engine):
    df = pd.read_sql(
        "SELECT * FROM stg_customer_raw",
        engine
    )

    staging_count = len(df)

    cleaned_df = CustomerCleaner(df).clean()

    cleaned_df.to_sql(
        "cleaned_customers",
        engine,
        if_exists="replace",
        index=False
    )

    with engine.connect() as db:
        cleaned_count = db.execute(
            text("SELECT COUNT(*) FROM cleaned_customers")
        ).scalar()

    assert cleaned_count == staging_count

    return cleaned_df


def build_curated_tables(engine):
    with engine.begin() as connection:

        connection.execute(
            text("""
                INSERT INTO dim_contract (contract_type)
                SELECT DISTINCT contract
                FROM cleaned_customers
                WHERE contract IS NOT NULL
                AND contract NOT IN (
                    SELECT contract_type
                    FROM dim_contract
                )
            """)
        )

        connection.execute(
            text("""
                INSERT INTO dim_payment (payment_method)
                SELECT DISTINCT payment_method
                FROM cleaned_customers
                WHERE payment_method IS NOT NULL
                AND payment_method NOT IN (
                    SELECT payment_method
                    FROM dim_payment
                )
            """)
        )

        connection.execute(
            text("""
                INSERT INTO customers
                (
                    customer_id,
                    gender,
                    senior_citizen,
                    partner,
                    dependents,
                    internet_service
                )
                SELECT
                    customer_id,
                    gender,
                    senior_citizen,
                    partner,
                    dependents,
                    internet_service
                FROM cleaned_customers
            """)
        )

        connection.execute(
            text("""
                INSERT INTO fact_customer_account
                (
                    customer_id,
                    contract_id,
                    payment_id,
                    tenure,
                    monthly_charges,
                    total_charges,
                    churn
                )
                SELECT
                    c.customer_id,
                    dc.contract_id,
                    dp.payment_id,
                    c.tenure,
                    c.monthly_charges,
                    NULLIF(c.total_charges, ''),
                    c.churn
                FROM cleaned_customers c
                JOIN dim_contract dc
                    ON c.contract = dc.contract_type
                JOIN dim_payment dp
                    ON c.payment_method = dp.payment_method
            """)
        )


def quality_report(engine):
    with engine.connect() as db:

        total = db.execute(
            text("SELECT COUNT(*) FROM cleaned_customers")
        ).scalar()

        null_customer_id = db.execute(
            text("""
                SELECT COUNT(*)
                FROM cleaned_customers
                WHERE customer_id IS NULL
            """)
        ).scalar()

        null_monthly_charges = db.execute(
            text("""
                SELECT COUNT(*)
                FROM cleaned_customers
                WHERE monthly_charges IS NULL
            """)
        ).scalar()

        invalid_churn = db.execute(
            text("""
                SELECT COUNT(*)
                FROM cleaned_customers
                WHERE churn NOT IN ('Yes', 'No')
                OR churn IS NULL
            """)
        ).scalar()

        print(
            f"customer_id NULL check: "
            f"{'PASS' if null_customer_id == 0 else 'FAIL'} "
            f"({null_customer_id})"
        )

        print(
            f"monthly_charges NULL check: "
            f"{'PASS' if null_monthly_charges == 0 else 'FAIL'} "
            f"({null_monthly_charges})"
        )

        print(
            f"churn values check: "
            f"{'PASS' if invalid_churn == 0 else 'FAIL'} "
            f"({invalid_churn})"
        )

        print(f"cleaned_customers row count: {total}")


def verify_curated_tables(engine):
    tables = [
        "dim_contract",
        "dim_payment",
        "customers",
        "fact_customer_account"
    ]

    with engine.connect() as db:
        for table in tables:
            count = db.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            ).scalar()

            print(
                f"{table}: "
                f"{'PASS' if count > 0 else 'FAIL'} "
                f"({count} rows)"
            )


if __name__ == "__main__":
    cleaned_df = clean_staging(engine)

    quality_report(engine)

    build_curated_tables(engine)

    verify_curated_tables(engine)