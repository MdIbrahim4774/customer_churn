import pandas as pd
from customer_cleaner import CustomerCleaner

# Loading data
df = pd.read_csv("Telco-Customer-Churn.csv")
df = CustomerCleaner(df).clean()

# Churn rate by contract_type
print("\n" + "=" * 30)
print("Contract Churn")
print("=" * 30)
contract_churn = df.groupby("contract")["churn"].mean().sort_values(ascending=False) * 100
print(contract_churn.round(2))

# Churn rate by service
print("\n" + "=" * 30)
print("Service Churn")
print("=" * 30)
service_churn = df.groupby("internet_service")["churn"].mean().sort_values(ascending=False) * 100
print(service_churn.round(2))

# Churn rate by payment method.
print("\n" + "=" * 30)
print("Payment Churn")
print("=" * 30)
payment_churn = df.groupby("payment_method")["churn"].mean().sort_values(ascending=False) * 100
print(payment_churn.round(2))

# Create tenure bucket
print("\n" + "=" * 30)
print("Tenure Bucket Churn")
print("=" * 30)
df["tenure_bucket"] = pd.cut(df['tenure'],bins=[0,12,24,48,72],labels=["0-12","13-24","25-48","49-72"])
tenure_churn = df.groupby("tenure_bucket")["churn"].mean().sort_values(ascending=False) * 100
print(tenure_churn.round(2))

# Avg monthly charges
print("\n" + "=" * 30)
print("Average Monthly Churn")
print("=" * 30)
avg_monthly_churn = df.groupby("churn")["monthly_charges"].mean()
avg_monthly_churn.index=["Non-Churn","Churn"]
print(avg_monthly_churn.round(2))

# Contract + internet
print("\n" + "=" * 30)
print("Combination Churn")
print("=" * 30)
Contract_Internet_Churn = df.groupby(["contract","internet_service"])["churn"].mean() *100
print(Contract_Internet_Churn.round(2))

highest_combo= Contract_Internet_Churn.idxmax()
print(highest_combo)

summary = ['\n1. Customers on Month-to-month contracts show the highest churn rate, making them the most vulnerable customer segment.',
 
'\n2. Customers using Fiber optic internet and Electronic Check payment methods also experience higher churn compared to other groups.',
 
'\n3. The retention team should prioritize these high-risk customers with targeted discounts, loyalty rewards, proactive customer support, and long-term contract offers to improve customer retention.']

print(*summary)