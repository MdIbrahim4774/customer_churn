import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import os
import joblib

engine = create_engine(
    "mysql+pymysql://root:root@localhost/customer_churn"
)

df = pd.read_sql(
    "SELECT * FROM customer_ml_features",
    engine
)

target = "churn"
drop_column = "customer_id"

categorical_columns = [
    "contract",
    "internet_service"
]

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

X = df[numeric_columns + categorical_columns]
y = df[target]

X = pd.get_dummies(
    X,
    columns=categorical_columns,
    dtype=int
)

print("Feature columns:")
print(X.columns.tolist())

print("X shape:", X.shape)
print("y shape:", y.shape)

print("Class balance:")
print(y.value_counts(normalize=True))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

logistic_model = LogisticRegression(
    max_iter=1000
)

tree_model = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)

logistic_model.fit(X_train, y_train)
tree_model.fit(X_train, y_train)

os.makedirs("models", exist_ok=True)

joblib.dump(
    logistic_model,
    "models/logistic_churn.pkl"
)

joblib.dump(
    tree_model,
    "models/tree_churn.pkl"
)

print("Models saved successfully.")

logistic_predictions = logistic_model.predict(X_test)
tree_predictions = tree_model.predict(X_test)

print("LOGISTIC REGRESSION")
print(
    classification_report(
        y_test,
        logistic_predictions,
        target_names=["Active", "Churned"]
    )
)

print("Confusion Matrix")
print(
    confusion_matrix(
        y_test,
        logistic_predictions
    )
)

print("DECISION TREE")
print(
    classification_report(
        y_test,
        tree_predictions,
        target_names=["Active", "Churned"]
    )
)

print("Confusion Matrix")
print(
    confusion_matrix(
        y_test,
        tree_predictions
    )
)

logistic_cv = cross_val_score(
    logistic_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

tree_cv = cross_val_score(
    tree_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

logistic_report = classification_report(
    y_test,
    logistic_predictions,
    output_dict=True
)

tree_report = classification_report(
    y_test,
    tree_predictions,
    output_dict=True
)

comparison = pd.DataFrame([
    {
        "Model": "Logistic Regression",
        "Accuracy": accuracy_score(
            y_test,
            logistic_predictions
        ),
        "Precision (Churned)": logistic_report["1"]["precision"],
        "Recall (Churned)": logistic_report["1"]["recall"],
        "F1 (Churned)": logistic_report["1"]["f1-score"],
        "CV F1": logistic_cv.mean()
    },
    {
        "Model": "Decision Tree",
        "Accuracy": accuracy_score(
            y_test,
            tree_predictions
        ),
        "Precision (Churned)": tree_report["1"]["precision"],
        "Recall (Churned)": tree_report["1"]["recall"],
        "F1 (Churned)": tree_report["1"]["f1-score"],
        "CV F1": tree_cv.mean()
    }
])

print("MODEL COMPARISON")
print(comparison.round(4))

best_model = comparison.loc[
    comparison["F1 (Churned)"].idxmax()
]

print(
    "Selected Model:",
    best_model["Model"]
)

print(
    "Reason: Higher F1 score for the Churned class:",
    round(best_model["F1 (Churned)"], 4)
)