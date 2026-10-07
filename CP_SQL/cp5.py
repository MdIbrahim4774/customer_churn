"""
74
CREATE TABLE customer_ml_features (
    customer_id VARCHAR(20) PRIMARY KEY,
    tenure INT NOT NULL,
    monthly_charges FLOAT NOT NULL,
    total_charges FLOAT NOT NULL,
    tenure_bucket VARCHAR(10) NOT NULL,
    service_count INT NOT NULL,
    high_charge_flag INT NOT NULL,
    is_long_term_customer INT NOT NULL,
    has_streaming_bundle INT NOT NULL,
    auto_pay_flag INT NOT NULL,
    churn INT NOT NULL
);

76 to 80
INSERT INTO customer_ml_features (
    customer_id,
    tenure,
    monthly_charges,
    total_charges,
    tenure_bucket,
    service_count,
    high_charge_flag,
    is_long_term_customer,
    has_streaming_bundle,
    auto_pay_flag,
    churn
)
SELECT
    f.customer_id,
    f.tenure,
    COALESCE(f.monthly_charges, 0),
    COALESCE(f.total_charges, 0),
    CASE
        WHEN f.tenure >= 0 AND f.tenure <= 12 THEN '0-12'
        WHEN f.tenure > 12 AND f.tenure <= 24 THEN '13-24'
        WHEN f.tenure > 24 AND f.tenure <= 48 THEN '25-48'
        WHEN f.tenure > 48 AND f.tenure <= 72 THEN '49-72'
    END AS tenure_bucket,
    CASE WHEN r.OnlineSecurity = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN r.OnlineBackup = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN r.DeviceProtection = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN r.TechSupport = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN r.StreamingTV = 'Yes' THEN 1 ELSE 0 END
    + CASE WHEN r.StreamingMovies = 'Yes' THEN 1 ELSE 0 END AS service_count,
    CASE
        WHEN COALESCE(f.monthly_charges, 0) > (
            SELECT AVG(COALESCE(monthly_charges, 0))
            FROM fact_customer_account
        )
        THEN 1
        ELSE 0
    END AS high_charge_flag,
    CASE
        WHEN f.tenure >= 24 THEN 1
        ELSE 0
    END AS is_long_term_customer,
    CASE
        WHEN r.StreamingTV = 'Yes'
        AND r.StreamingMovies = 'Yes'
        THEN 1
        ELSE 0
    END AS has_streaming_bundle,
    CASE
        WHEN dp.payment_method LIKE '%automatic%' THEN 1
        ELSE 0
    END AS auto_pay_flag,
    f.churn
FROM fact_customer_account f
JOIN dim_payment dp
    ON f.payment_id = dp.payment_id
JOIN stg_customer_raw r
    ON f.customer_id = r.customerID;

81

SELECT COUNT(*) AS total_records
FROM customer_ml_features;

SELECT COUNT(*) AS null_monthly_charges
FROM customer_ml_features
WHERE monthly_charges IS NULL;


82

SELECT churn, COUNT(*)
FROM customer_ml_features
GROUP BY churn;

"""