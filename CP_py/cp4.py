import pandas as pd
from customer_cleaner import CustomerCleaner

df = CustomerCleaner(pd.read_csv("Telco-Customer-Churn.csv"))\
    .clean()

def add_tenure_bucket(df):
    df["tenure_bucket"] = pd.cut(
        df['tenure'],
        bins=[0,12,24,48,72],
        labels=["0-12","13-24","25-48","49-72"]
        )
    
    tenure_churn = df.groupby("tenure_bucket")["churn"].mean() * 100
    print(tenure_churn.round(2))

def add_high_charge_flag(df):
    median_monthly_charge = df["monthly_charges"].median()
    df["high_charge_flag"] = df["monthly_charges"].apply(lambda x: 1 if x>median_monthly_charge else 0)

def add_service_count(df):
    to_check = ['online_security', 'online_backup', 'device_protection', 'tech_support', 'streaming_tv', 'streaming_movies']
    for col in to_check:
        df[col] = df[col].replace({
            "Yes": 1,
            "No" : 0,
            "No internet service" : 0
        })
    df["service_count"] = df[to_check].sum(axis=1)

def add_is_long_term_cust(df):
    df["is_long_term_customer"] = df["tenure"].apply(lambda x: 1 if x>=24 else 0)

def add_has_streaming_bundle(df):
    to_check = ['streaming_tv', 'streaming_movies']
    for col in to_check:
            df[col] = df[col].replace({
                "Yes": 1,
                "No" : 0,
                "No internet service" : 0
            })
    df["has_streaming_bundle"] = ((df["streaming_tv"] == 1) & (df["streaming_movies"]==1)).astype(int)

def add_auto_pay_flag(df):
     df["auto_pay_flag"] = df["payment_method"].str.contains("automatic").astype(int)

def build_features(df):
    add_tenure_bucket(df)
    add_high_charge_flag(df)
    add_service_count(df)
    add_is_long_term_cust(df)
    add_has_streaming_bundle(df)
    add_auto_pay_flag(df)

if __name__ == "__main__":
    build_features(df)
    print(df["high_charge_flag"].corr(df["churn"]))
    print(df["service_count"].corr(df["churn"]))
    print(df["is_long_term_customer"].corr(df["churn"]))
    print(df["has_streaming_bundle"].corr(df["churn"]))
    print(df["auto_pay_flag"].corr(df["churn"]))

    df.to_csv("customer_features.csv")
    print("Customer features saved to customer_features.csv")

