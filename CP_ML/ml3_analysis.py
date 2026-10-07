import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:root@localhost/customer_churn"
)

df = pd.read_sql(
    "SELECT * FROM customer_ml_features",
    engine
)

target = "churn"
drop_column = "customer_id"

numeric_columns = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "auto_pay_flag",
    "has_streaming_bundle"
]

categorical_columns = [
    "contract",
    "internet_service"
]

X = df[numeric_columns + categorical_columns]
y = df[target]

X = pd.get_dummies(
    X,
    columns=categorical_columns,
    dtype=int
)

customer_ids = df["customer_id"]

model = joblib.load(
    "models/tree_churn.pkl"
)

print("Model loaded successfully.")

feature_names = X.columns

coefficients = pd.Series(
    model.feature_importances_,
    index=feature_names
)

coefficient_table = pd.DataFrame({
    "feature": coefficients.index,
    "coefficient": coefficients.values,
    "absolute_value": coefficients.abs().values
})

coefficient_table = coefficient_table.sort_values(
    "absolute_value",
    ascending=False
)

print("\nTop Features by Logistic Regression Coefficient")
print(
    coefficient_table[
        ["feature", "coefficient"]
    ].head(10)
)

top_10 = coefficient_table.head(10).sort_values(
    "coefficient"
)

plt.figure(figsize=(10, 6))
plt.barh(
    top_10["feature"],
    top_10["coefficient"]
)
plt.xlabel("Coefficient")
plt.ylabel("Feature")
plt.title("Top 10 Logistic Regression Features")
plt.tight_layout()
plt.show()

churn_probability = model.predict_proba(X)[:, 1]

scored_customers = pd.DataFrame({
    "customer_id": customer_ids,
    "churn_probability": churn_probability
})

top_20 = scored_customers.sort_values(
    "churn_probability",
    ascending=False
).head(20)

print("\nTop 20 Highest-Risk Customers")
print(top_20.to_string(index=False))

top_3_positive = coefficient_table[
    coefficient_table["coefficient"] > 0
].head(3)

print("\nTop 3 Features Associated With Higher Churn")
print(
    top_3_positive[
        ["feature", "coefficient"]
    ]
)

high_risk = pd.read_sql(
    """
    SELECT customer_id
    FROM v_high_risk_customers
    """,
    engine
)

ml_top_ids = set(top_20["customer_id"])
rule_based_ids = set(high_risk["customer_id"])

overlap = ml_top_ids.intersection(rule_based_ids)

print("\nRule-Based / ML Overlap")
print("ML top 20:", len(ml_top_ids))
print("Rule-based high-risk:", len(rule_based_ids))
print("Overlap:", len(overlap))
print("Overlap percentage:", round(
    len(overlap) / len(ml_top_ids) * 100,
    2
), "%")