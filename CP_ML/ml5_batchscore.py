import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from ml4_predict import predict_churn

engine = create_engine(
    "mysql+pymysql://root:root@localhost/customer_churn"
)

df = pd.read_sql(
    "SELECT * FROM customer_ml_features",
    engine
)

def score_customer(row):
    result = predict_churn(
        tenure=int(row["tenure"]),
        monthly_charges=float(row["monthly_charges"]),
        contract_type=row["contract"],
        service_count=int(row["service_count"]),
        internet_service=row["internet_service"]
    )

    return pd.Series({
        "risk_score": result["risk_score"],
        "prediction": result["prediction"],
        "confidence": result["confidence"]
    })

scores = df.apply(
    score_customer,
    axis=1
)

df["risk_score"] = scores["risk_score"]
df["prediction"] = scores["prediction"]
df["confidence"] = scores["confidence"]

df["scoring_date"] = datetime.today().strftime("%Y-%m-%d")

risk_table = df[
    [
        "customer_id",
        "risk_score",
        "prediction",
        "confidence",
        "scoring_date"
    ]
]

risk_table.to_sql(
    "customer_risk_table",
    engine,
    if_exists="replace",
    index=False
)

print("Batch scoring completed.")
print("Total customers:", len(risk_table))

print("\nPrediction Summary")
print(
    risk_table["prediction"].value_counts()
)

print("\nPrediction Percentage")
print(
    risk_table["prediction"].value_counts(
        normalize=True
    ).mul(100).round(2)
)

print("\nTop 10 Highest-Risk Customers")
print(
    risk_table
    .sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)