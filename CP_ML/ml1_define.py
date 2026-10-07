import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:root@localhost/customer_churn"
)

df = pd.read_sql(
    "SELECT * FROM customer_ml_features",
    engine
)

print("Dataset shape:", df.shape)

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

X = df.drop(columns=[target, drop_column])
y = df[target]

X = pd.get_dummies(
    X,
    columns=categorical_columns,
    dtype=int
)

print("\nFeature columns:")
print(X.columns.tolist())

print("\nX:")
print(X.head())

print("\nX shape:", X.shape)

print("\ny:")
print(y.head())

print("\ny shape:", y.shape)

print("\nClass balance:")
print(y.value_counts(normalize=True))

print("\nClass counts:")
print(y.value_counts())