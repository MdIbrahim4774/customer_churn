'''
67

SELECT
    dc.contract_type,
    ROUND(AVG(fca.churn) * 100, 2) AS churn_rate
FROM fact_customer_account fca
JOIN dim_contract dc
    ON fca.contract_id = dc.contract_id
GROUP BY dc.contract_type
ORDER BY churn_rate DESC;

68

SELECT
    dp.payment_method,
    ROUND(AVG(fca.churn) * 100, 2) AS churn_rate
FROM fact_customer_account fca
JOIN dim_payment dp
    ON fca.payment_id = dp.payment_id
GROUP BY dp.payment_method
ORDER BY churn_rate DESC;

69

SELECT
    churn,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM fact_customer_account
GROUP BY churn
ORDER BY churn;

70

SELECT
    COUNT(*) AS high_risk_customer_count
FROM fact_customer_account fca
JOIN dim_contract dc
    ON fca.contract_id = dc.contract_id
WHERE dc.contract_type = 'Month-to-month'
AND fca.tenure < 12
AND fca.monthly_charges > (
    SELECT AVG(monthly_charges)
    FROM fact_customer_account
);

71

SELECT
    COUNT(*) AS high_value_churned_customers,
    ROUND(AVG(tenure), 2) AS average_tenure
FROM fact_customer_account
WHERE churn = 1
AND total_charges > 2000;


72




73

SELECT
    dc.contract_type,
    ROUND(AVG(fca.monthly_charges), 2) AS avg_monthly_charges,
    ROUND(AVG(fca.tenure), 2) AS avg_tenure,
    ROUND(AVG(fca.churn) * 100, 2) AS churn_rate
FROM fact_customer_account fca
JOIN dim_contract dc
    ON fca.contract_id = dc.contract_id
GROUP BY dc.contract_type
ORDER BY churn_rate DESC;
'''