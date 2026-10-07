from sqlalchemy import text


def get_churn_summary(db):
    total_query = text("""
        SELECT
            COUNT(*) AS total_customers,
            SUM(churn) AS total_churned,
            AVG(churn) AS churn_rate
        FROM fact_customer_account
    """)

    total_result = db.execute(total_query).mappings().first()

    contract_query = text("""
        SELECT
            dc.contract_type,
            AVG(f.churn) AS churn_rate
        FROM fact_customer_account f
        JOIN dim_contract dc
            ON f.contract_id = dc.contract_id
        GROUP BY dc.contract_type
        ORDER BY churn_rate DESC
    """)

    contract_results = db.execute(contract_query).mappings().all()

    internet_query = text("""
        SELECT
            c.internet_service,
            AVG(f.churn) AS churn_rate
        FROM fact_customer_account f
        JOIN customers c
            ON f.customer_id = c.customer_id
        GROUP BY c.internet_service
        ORDER BY churn_rate DESC
    """)

    internet_results = db.execute(internet_query).mappings().all()

    return {
        "total_customers": total_result["total_customers"],
        "total_churned": total_result["total_churned"],
        "churn_rate": round(float(total_result["churn_rate"]), 4),
        "by_contract": [
            {
                "contract_type": row["contract_type"],
                "churn_rate": round(float(row["churn_rate"]), 4)
            }
            for row in contract_results
        ],
        "by_internet_service": [
            {
                "internet_service": row["internet_service"],
                "churn_rate": round(float(row["churn_rate"]), 4)
            }
            for row in internet_results
        ]
    }

def get_high_risk_customers(db, limit: int = 50, min_tenure: int = None, max_tenure: int = None):
    query = """
        SELECT
            customer_id,
            tenure,
            monthly_charges,
            contract_type,
            risk_reason
        FROM v_high_risk_customers
        WHERE 1 = 1
    """
    
    params = {}
    if min_tenure is not None:
        query += " AND tenure >= :min_tenure"
        params["min_tenure"] = min_tenure

    if max_tenure is not None:
        query += " AND tenure <= :max_tenure"
        params["max_tenure"] = max_tenure

    query += """
        ORDER BY monthly_charges DESC
        LIMIT :limit
    """

    params["limit"] = limit

    result = db.execute(
        text(query),
        params
    ).mappings().all()

    return result

def get_customer_features(db, customer_id: str):
    query = text("""
        SELECT
            customer_id,service_count, 
            tenure_bucket, 
            high_charge_flag, 
            is_long_term_customer, 
            has_streaming_bundle, 
            auto_pay_flag, 
            monthly_charges, 
            total_charges FROM customer_ml_features
            WHERE customer_id = :customer_id;
    """)

    result = db.execute(
        query,
        {"customer_id": customer_id}
    ).mappings().first()

    return result