import joblib
import pandas as pd

model = joblib.load("models/tree_churn.pkl")

TRAINING_COLUMNS = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "auto_pay_flag",
    "has_streaming_bundle",
    "contract_Month-to-month",
    "contract_One year",
    "contract_Two year",
    "internet_service_DSL",
    "internet_service_Fiber optic",
    "internet_service_No"
]

def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    service_count,
    internet_service
):
    high_charge_flag = 1 if monthly_charges > 64.76 else 0
    is_long_term_customer = 1 if tenure >= 24 else 0

    data = {
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "total_charges": monthly_charges * tenure,
        "service_count": service_count,
        "high_charge_flag": high_charge_flag,
        "is_long_term_customer": is_long_term_customer,
        "auto_pay_flag": 0,
        "has_streaming_bundle": 0,
        "contract_Month-to-month": 0,
        "contract_One year": 0,
        "contract_Two year": 0,
        "internet_service_DSL": 0,
        "internet_service_Fiber optic": 0,
        "internet_service_No": 0
    }

    contract_column = f"contract_{contract_type}"
    internet_column = f"internet_service_{internet_service}"

    if contract_column in data:
        data[contract_column] = 1

    if internet_column in data:
        data[internet_column] = 1

    df = pd.DataFrame([data])

    df = df.reindex(
        columns=TRAINING_COLUMNS,
        fill_value=0
    )

    return df


def predict_churn(
    tenure,
    monthly_charges,
    contract_type,
    service_count,
    internet_service
):
    X = preprocess_input(
        tenure,
        monthly_charges,
        contract_type,
        service_count,
        internet_service
    )

    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0][1]

    if prediction == 1:
        prediction_text = "Likely to churn"
    else:
        prediction_text = "Unlikely to churn"

    confidence = max(
        model.predict_proba(X)[0]
    )

    return {
        "risk_score": float(probability),
        "prediction": str(prediction),
        "confidence": float(confidence)
    }