from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)

import os
os.environ["HADOOP_HOME"] = r"C:\Users\ibrahim.m\Documents\Notes\hadoop"
os.environ["PATH"] = os.environ["PATH"] + r";C:\Users\ibrahim.m\Documents\Notes\hadoop\bin"

spark = (
    SparkSession.builder
    .appName("CustomerChurnDE5")
    .master("local[2]")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)

schema = StructType([
    StructField("customerID", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("SeniorCitizen", IntegerType(), True),
    StructField("Partner", StringType(), True),
    StructField("Dependents", StringType(), True),
    StructField("tenure", IntegerType(), True),
    StructField("PhoneService", StringType(), True),
    StructField("MultipleLines", StringType(), True),
    StructField("InternetService", StringType(), True),
    StructField("OnlineSecurity", StringType(), True),
    StructField("OnlineBackup", StringType(), True),
    StructField("DeviceProtection", StringType(), True),
    StructField("TechSupport", StringType(), True),
    StructField("StreamingTV", StringType(), True),
    StructField("StreamingMovies", StringType(), True),
    StructField("Contract", StringType(), True),
    StructField("PaperlessBilling", StringType(), True),
    StructField("PaymentMethod", StringType(), True),
    StructField("MonthlyCharges", DoubleType(), True),
    StructField("TotalCharges", StringType(), True),
    StructField("Churn", StringType(), True)
])

df = (
    spark.read
    .option("header", True)
    .schema(schema)
    .csv(r"C:\Users\ibrahim.m\Documents\Notes\Project\customer_pipeline\data\raw\Telco-Customer-Churn.csv")
)

print("Original Schema")
df.printSchema()

df = df.withColumn(
    "TotalCharges",
    F.regexp_replace(F.col("TotalCharges"), r"^\s*$", "")
)

df = df.withColumn(
    "TotalCharges",
    F.col("TotalCharges").cast(DoubleType())
)

df = df.withColumn(
    "churn_encoded",
    F.when(F.col("Churn") == "Yes", 1).otherwise(0)
)

print("Schema After Cleaning")
df.printSchema()

print("Contract Summary")

contract_summary = (
    df.groupBy("Contract")
    .agg(
        F.count("*").alias("customer_count"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy(F.col("churn_rate").desc())
)

contract_summary.show()

print("Internet Service Summary")

internet_summary = (
    df.groupBy("InternetService")
    .agg(
        F.avg("MonthlyCharges").alias("avg_monthly_charges"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy(F.col("churn_rate").desc())
)

internet_summary.show()

print("Contract Summary with Percentage")

contract_summary.select(
    "Contract",
    "customer_count",
    "churn_rate",
    (F.col("churn_rate") * 100).alias("churn_percentage")
).show()

output_path =r"C:\Users\ibrahim.m\Documents\Notes\Project\customer_pipeline\data\spark_output\contract_summary"
contract_summary.write.mode("overwrite").partitionBy(
    "Contract"
).parquet(output_path)


parquet_df = spark.read.parquet(
    output_path
)

print("Parquet Schema")
parquet_df.printSchema()

print("Parquet Count")
print(parquet_df.count())

spark.stop()