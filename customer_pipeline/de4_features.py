import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"

engine = create_engine(DATABASE_URL)

FEATURE_COLUMNS = [
    "tenure_bucket",
    "high_charge_flag",
    "service_count",
    "is_long_term_customer",
    "has_streaming_bundle",
    "auto_pay_flag"
]


def build_features(engine):
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    average_monthly_charge = df["monthly_charges"].mean()

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[-1, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"]
    )

    service_columns = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]

    for column in service_columns:
        df[column] = df[column].replace({
            "Yes": 1,
            "No": 0,
            "No internet service": 0
        })

    df["service_count"] = df[service_columns].sum(axis=1)

    df["high_charge_flag"] = (
        df["monthly_charges"] > average_monthly_charge
    ).astype(int)

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)

    df["has_streaming_bundle"] = (
        (df["streaming_tv"] == 1) &
        (df["streaming_movies"] == 1)
    ).astype(int)

    df["auto_pay_flag"] = (
        df["payment_method"]
        .str.contains("automatic", case=False, na=False)
        .astype(int)
    )

    df["total_charges"] = pd.to_numeric(
        df["total_charges"],
        errors="coerce"
    ).fillna(0)

    feature_df = df[
        [
            "customer_id",
            "gender",
            "senior_citizen",
            "partner",
            "dependents",
            "tenure",
            "monthly_charges",
            "total_charges",
            "contract",
            "payment_method",
            "internet_service",
            "tenure_bucket",
            "service_count",
            "high_charge_flag",
            "is_long_term_customer",
            "has_streaming_bundle",
            "auto_pay_flag",
            "churn"
        ]
    ]

    feature_df.to_sql(
        "customer_ml_features",
        engine,
        if_exists="replace",
        index=False
    )

    print(f"Average monthly charges: {average_monthly_charge:.2f}")

    return average_monthly_charge

def validate_features(engine):
    with engine.connect() as connection:

        cleaned_count = connection.execute(
            text("SELECT COUNT(*) FROM cleaned_customers")
        ).scalar()

        feature_count = connection.execute(
            text("SELECT COUNT(*) FROM customer_ml_features")
        ).scalar()

        assert feature_count == cleaned_count

        print(
            f"Row count check: "
            f"{'PASS' if feature_count == cleaned_count else 'FAIL'} "
            f"({feature_count}/{cleaned_count})"
        )

        for column in FEATURE_COLUMNS:
            null_count = connection.execute(
                text(
                    f"""
                    SELECT COUNT(*)
                    FROM customer_ml_features
                    WHERE {column} IS NULL
                    """
                )
            ).scalar()

            print(
                f"{column} NULL check: "
                f"{'PASS' if null_count == 0 else 'FAIL'} "
                f"({null_count})"
            )


if __name__ == "__main__":
    median = build_features(engine)

    print(f"Median monthly charges: {median:.2f}")

    validate_features(engine)