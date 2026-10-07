# #CP1-1
import pandas as pd
df = pd.read_csv("Telco-Customer-Churn.csv")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

#CP1-2      Datatypes
print("\n" + "=" * 30)
print("Columns and Data Types")
print("=" * 30)
print(df.dtypes)

#CP1-3      Null value abd null percentage
print("\n" + "=" * 30)
print("Missing Values")
print("=" * 30)

null_counts = df.isnull().sum()
null_percent = (null_counts / len(df)) * 100

missing_percentage = pd.DataFrame({
    "Null Count": null_counts,
    "Null %": null_percent.round(2)
})

print(missing_percentage)

#CP1-4      profile important categorical columns
cat_cols = ["gender", "Partner", 'Dependents', 'PhoneService', 'InternetService', 'Contract', 'PaymentMethod', 'Churn']

print("\n" + "=" * 30)
print("Categorical Column Summary")
print("=" * 30)

for col in cat_cols:
    if col in df.columns:
        print(f"\n--- ={col}= ---")
        print("Unique values:")
        print(df[col].unique())
        print("\nValue counts:")
        print(df[col].value_counts(dropna=False))

#CP1-5      Churn distribution and churn rate
print("\n" + "=" * 30)
print("Churn Distribution")
print("=" * 30)

if "Churn" in df.columns:
    churn_counts = df["Churn"].value_counts()
    print(churn_counts)

    churn_rate = (df["Churn"].eq("Yes").mean()) * 100
    print(f"\nChurn Rate: {churn_rate:.2f}%")

#CP1-6      Inspect TotalCharges
TotalCDT = df["TotalCharges"].dtype
null_values = pd.to_numeric(df["TotalCharges"], errors='coerce').isna().sum()

print("\n" + "=" * 30)
print("Inspect TotalCharge")
print("=" * 30)

TotalChargeData = {"DataType": TotalCDT, "Null Values": null_values}

print("DataType:", TotalCDT, "\nNull Values:", null_values)


#CP1-7
print("\n" + "=" * 30)
print("Numerical Statistics")
print("=" * 30)

print("\ntenure:")
print(f"Minimum : {df['tenure'].min()}")
print(f"Maximum : {df['tenure'].max()}")
print(f"Mean : {df['tenure'].mean():.2f}")

print("\nTotalCharges:")

print(f"Minimum : {df['TotalCharges'].min()}")
print(f"Maximum : {df['TotalCharges'].max()}")
print(f"Mean : {pd.to_numeric(df['TotalCharges'], errors='coerce').mean():.2f}")

print("\nMonthlyCharges:")
print(f"Minimum : {df['MonthlyCharges'].min()}")
print(f"Maximum : {df['MonthlyCharges'].max()}")
print(f"Mean : {pd.to_numeric(df['MonthlyCharges'], errors='coerce').mean():.2f}")



#CP1-8      Profile summary
print("\n" + "=" * 30)
print("Profiling Summary")
print("=" * 30)


summary = [
    "Each row represents a unique customer, with demographic, service, account, billing, and churn information.",
    "The dataset contains both numerical (e.g., tenure, MonthlyCharges, TotalCharges) and categorical variables that require different preprocessing techniques.",
    "The 'TotalCharges' column may contain blank values for customers with zero tenure; treat these as missing values before analysis.",
    "The target variable 'Churn' is binary ('Yes'/'No') and may be moderately imbalanced, so use evaluation metrics beyond accuracy when building models.",
    "Identifier columns such as 'customerID' should be excluded from modeling, and categorical features should be encoded before training machine learning models."
]

for item in summary:
    print(item)