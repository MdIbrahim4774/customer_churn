"""
83

Contract = Month-to-month
AND
Tenure < 12
AND
Monthly Charges > dataset average


84

SELECT
    f.customer_id,
    f.tenure,
    f.monthly_charges,
    dc.contract_type,
    'Month-to-month contract, tenure below 12 months, monthly charges above dataset average' AS risk_reason
FROM fact_customer_account f
JOIN dim_contract dc
    ON f.contract_id = dc.contract_id
WHERE dc.contract_type = 'Month-to-month'
  AND f.tenure < 12
  AND f.monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM fact_customer_account
  ) LIMIT 5;

85

SELECT COUNT(*) AS high_risk_count
FROM fact_customer_account f
JOIN dim_contract dc
    ON f.contract_id = dc.contract_id
WHERE dc.contract_type = 'Month-to-month'
  AND f.tenure < 12
  AND f.monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM fact_customer_account
  );

SELECT
    f.customer_id,
    f.tenure,
    f.monthly_charges,
    dc.contract_type
FROM fact_customer_account f
JOIN dim_contract dc
    ON f.contract_id = dc.contract_id
WHERE dc.contract_type = 'Month-to-month'
  AND f.tenure < 12
  AND f.monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM fact_customer_account
  )
LIMIT 10;


86

CREATE VIEW v_high_risk_customers AS
SELECT
    f.customer_id,
    f.tenure,
    f.monthly_charges,
    dc.contract_type,
    'Month-to-month contract, tenure below 12 months, monthly charges above dataset average' AS risk_reason
FROM fact_customer_account f
JOIN dim_contract dc
    ON f.contract_id = dc.contract_id
WHERE dc.contract_type = 'Month-to-month'
  AND f.tenure < 12
  AND f.monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM fact_customer_account
  );

87

SELECT *
FROM v_high_risk_customers
LIMIT 5;

88


SELECT
COUNT(*) AS high_risk_count,
(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_customer_account)) AS high_risk_percentage
FROM v_high_risk_customers;

89

Rule-based scoring is simple, transparent, and easy for the retention team to understand and act on immediately. However, fixed rules can miss complex relationships between multiple customer attributes and may incorrectly classify customers near the thresholds. ML-based scoring can learn patterns from historical churn data and combine many features to produce more flexible risk predictions, but it is more complex and may be less explainable.

"""