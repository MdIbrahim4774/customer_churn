import logging
from customer_cleaner import CustomerCleaner
from cp4 import *
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_data(filepath):
    try:
        logger.info("Starting data load: %s", filepath)
        df = pd.read_csv(filepath)
        logger.info("Data loaded successfully: Row count %s", len(df))
        return df
    except Exception as e:
        logger.error("Failed to load data: %s", e)
        raise

def build_features(df):
    try:
        logger.info("Starting Feature Engineering.")
        add_tenure_bucket(df)
        add_high_charge_flag(df)
        add_service_count(df)
        add_is_long_term_cust(df)
        add_has_streaming_bundle(df)
        add_auto_pay_flag(df)
        logger.info("Feature engineering successful")
        return df

    except Exception as e:
        logger.error("Failed to produce Feature Engineering.")
        raise

def save_outputs(clean_df, feature_df, output_dir = "./"):
    try:
        logger.info("Starting output save.")
        timestamp = datetime.now().strftime("%Y%m%d")
        clear_path = f"{output_dir}/cleaned_customer_data_{timestamp}.csv"
        feature_path = f"{output_dir}/featured_customer_data_{timestamp}.csv"
        clean_df.to_csv(clear_path, index=False)
        feature_df.to_csv(feature_path, index=False)
        logging.info("Cleaned data saved: %s", clear_path)
        logging.info("Featured data saved: %s", feature_path)
        return clear_path, feature_path

    except Exception as e:
        logger.error("Failed to save outputs: %s", e)
        raise

def validate_data_quality(df):
    try:
        logger.info("Validating data quality")
        assert not df["monthly_charges"].isnull().any(), (
            "Data quality check failed: monthly_charges contains null values."
        )

        churn_vals = set(df["churn"].unique())
        assert churn_vals.issubset({1,0}), (
            "Data quality check failed: Churn is invalid"
        )
        logger.info("All data quality checks passed.")
        


    except Exception as e:
        logger.error("Data quality validation failed: %s", e)
        raise

def main():
    start_time = datetime.now()

    logger.info("=" * 60)
    logger.info("CUSTOMER PIPELINE STARTED")
    logger.info("Start time: %s", start_time)
    logger.info("=" * 60)

    input_file = "Telco-Customer-Churn.csv"
    output_dir = "."

    df = load_data(input_file)
    clean_df = CustomerCleaner(df).clean()
    feature_df = build_features(clean_df.copy())
    validate_data_quality(feature_df)
    cleaned_path, features_path = save_outputs(
            clean_df,
            feature_df,
            output_dir
        )

    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("=" * 30)
    logger.info("CUSTOMER PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("End time: %s", end_time)
    logger.info("Duration: %s", duration)
    logger.info("Cleaned output: %s", cleaned_path)
    logger.info("Feature output: %s", features_path)
    logger.info("=" * 30)

if __name__ == "__main__":
    main()