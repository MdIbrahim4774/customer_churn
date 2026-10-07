import json
import logging
from datetime import datetime

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def check_null_rate(df, col, threshold):
    null_rate = df[col].isnull().mean() * 100
    passed = null_rate <= threshold

    return {
        "check_name": f"null_rate_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": round(null_rate, 2),
        "threshold": threshold
    }


def check_value_range(df, col, min_value=None, max_value=None):
    if min_value is not None:
        min_found = df[col].min()
        min_passed = min_found >= min_value
    else:
        min_found = None
        min_passed = True

    if max_value is not None:
        max_found = df[col].max()
        max_passed = max_found <= max_value
    else:
        max_found = None
        max_passed = True

    passed = min_passed and max_passed

    return {
        "check_name": f"value_range_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": {
            "min": min_found,
            "max": max_found
        },
        "threshold": {
            "min": min_value,
            "max": max_value
        }
    }


def check_allowed_values(df, col, allowed_set):
    found_values = set(df[col].dropna().unique())
    invalid_values = found_values - set(allowed_set)

    passed = len(invalid_values) == 0

    return {
        "check_name": f"allowed_values_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": sorted(found_values),
        "threshold": sorted(allowed_set),
        "invalid_values": sorted(invalid_values)
    }


def check_row_count(df, expected_min):
    row_count = len(df)
    passed = row_count >= expected_min

    return {
        "check_name": "row_count",
        "status": "PASS" if passed else "FAIL",
        "value_found": row_count,
        "threshold": expected_min
    }


def check_no_duplicates(df, key_col):
    duplicate_count = df[key_col].duplicated().sum()
    passed = duplicate_count == 0

    return {
        "check_name": f"duplicate_check_{key_col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(duplicate_count),
        "threshold": 0
    }


def check_churn_distribution(df):
    distribution = df["churn"].value_counts().to_dict()
    valid_values = {0, 1}

    found_values = set(df["churn"].dropna().unique())
    invalid_values = found_values - valid_values

    passed = len(invalid_values) == 0

    return {
        "check_name": "churn_distribution",
        "status": "PASS" if passed else "FAIL",
        "value_found": {
            str(key): int(value)
            for key, value in distribution.items()
        },
        "threshold": "churn values must be 0 or 1"
    }


def run_quality_checks(df):
    results = []

    results.append({
        **check_null_rate(df, "monthly_charges", 0),
        "severity": "CRITICAL"
    })

    results.append({
        **check_null_rate(df, "tenure", 0),
        "severity": "CRITICAL"
    })

    results.append({
        **check_value_range(df, "tenure", 0, 100),
        "severity": "CRITICAL"
    })

    results.append({
        **check_value_range(df, "monthly_charges", 0.01),
        "severity": "CRITICAL"
    })

    results.append({
        **check_allowed_values(
            df,
            "contract",
            {
                "Month-to-month",
                "One year",
                "Two year"
            }
        ),
        "severity": "CRITICAL"
    })

    results.append({
        **check_row_count(df, 7000),
        "severity": "WARNING"
    })

    results.append({
        **check_no_duplicates(df, "customer_id"),
        "severity": "CRITICAL"
    })

    results.append({
        **check_churn_distribution(df),
        "severity": "CRITICAL"
    })

    return results

def save_quality_report(results, output_path="quality_report.json"):
    report = {
        "generated_at": datetime.now().isoformat(),
        "checks": results
    }

    with open(output_path, "w") as file:
        json.dump(
            report,
            file,
            indent=4,
            default=str
        )


def validate_pipeline(df):
    results = run_quality_checks(df)

    save_quality_report(results)

    critical_failures = []
    warning_failures = []

    for result in results:
        if result["status"] == "PASS":
            logger.info(
                "%s [%s]: PASS",
                result["check_name"],
                result["severity"]
            )

        else:
            logger.error(
                "%s [%s]: FAIL",
                result["check_name"],
                result["severity"]
            )

            if result["severity"] == "CRITICAL":
                critical_failures.append(result["check_name"])

            elif result["severity"] == "WARNING":
                warning_failures.append(result["check_name"])

    if warning_failures:
        logger.warning(
            "Warning checks failed: %s",
            warning_failures
        )

    if critical_failures:
        raise ValueError(
            f"Critical data quality checks failed: {critical_failures}"
        )

    logger.info("All critical quality checks passed.")

    return results

if __name__ == "__main__":
    df = pd.read_csv("data/raw/Telco-Customer-Churn.csv")

    df.columns = [
        column.strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    df["customer_id"] = df["customerid"]

    df["monthly_charges"] = pd.to_numeric(
        df["monthlycharges"],
        errors="coerce"
    )

    df["tenure"] = pd.to_numeric(
        df["tenure"],
        errors="coerce"
    )

    df["contract"] = df["contract"]

    df["churn"] = df["churn"].map({
        "Yes": 1,
        "No": 0
    })

    validate_pipeline(df)