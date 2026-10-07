"""
59

CREATE TABLE dim_contract (
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    contract_type VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO dim_contract (contract_type)
SELECT DISTINCT Contract
FROM stg_customer_raw
WHERE Contract IS NOT NULL
AND Contract <> '';

SELECT *
FROM dim_contract
ORDER BY contract_id;

"""


"""
60

CREATE TABLE dim_payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO dim_payment (payment_method)
SELECT DISTINCT PaymentMethod
FROM stg_customer_raw
WHERE PaymentMethod IS NOT NULL
AND PaymentMethod <> '';

SELECT *
FROM dim_payment
ORDER BY payment_id;

"""

"""
61

CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen TINYINT NOT NULL,
    partner TINYINT NOT NULL,
    dependents TINYINT NOT NULL
);

INSERT INTO customers (
    customer_id,
    gender,
    senior_citizen,
    partner,
    dependents
)
SELECT
    TRIM(customerID),
    CASE
        WHEN LOWER(TRIM(gender)) = 'male' THEN 'Male'
        WHEN LOWER(TRIM(gender)) = 'female' THEN 'Female'
        ELSE NULL
    END,
    CASE
        WHEN SeniorCitizen = 1 THEN 1
        ELSE 0
    END,
    CASE
        WHEN LOWER(TRIM(Partner)) = 'yes' THEN 1
        ELSE 0
    END,
    CASE
        WHEN LOWER(TRIM(Dependents)) = 'yes' THEN 1
        ELSE 0
    END
FROM stg_customer_raw;


"""

"""
62

CREATE TABLE fact_customer_account (
    customer_id VARCHAR(20) PRIMARY KEY,
    contract_id INT NOT NULL,
    payment_id INT NOT NULL,
    tenure INT,
    monthly_charges DECIMAL(10,2),
    total_charges DECIMAL(12,2),
    churn TINYINT NOT NULL,
    CONSTRAINT fk_account_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),
    CONSTRAINT fk_account_contract
        FOREIGN KEY (contract_id)
        REFERENCES dim_contract(contract_id),
    CONSTRAINT fk_account_payment
        FOREIGN KEY (payment_id)
        REFERENCES dim_payment(payment_id)
);

INSERT INTO fact_customer_account (
    customer_id,
    contract_id,
    payment_id,
    tenure,
    monthly_charges,
    total_charges,
    churn
)
SELECT
    s.customerID,
    c.contract_id,
    p.payment_id,
    s.tenure,
    s.MonthlyCharges,
    CAST(NULLIF(TRIM(s.TotalCharges), '') AS DECIMAL(12,2)),
    CASE
        WHEN LOWER(TRIM(s.Churn)) = 'yes' THEN 1
        ELSE 0
    END
FROM stg_customer_raw s
JOIN dim_contract c
    ON TRIM(s.Contract) = c.contract_type
JOIN dim_payment p
    ON TRIM(s.PaymentMethod) = p.payment_method;


"""

"""
63

SELECT
    (SELECT COUNT(*) FROM dim_contract) AS contract_count,
    (SELECT COUNT(*) FROM dim_payment) AS payment_count,
    (SELECT COUNT(*) FROM customers) AS customer_count,
    (SELECT COUNT(*) FROM fact_customer_account) AS account_count;
"""

"""
64

SELECT
    c.customer_id, c.gender, c.partner, c.dependents,
    f.tenure, f.monthly_charges, f.total_charges, f.churn,
    dc.contract_type, dp.payment_method
FROM customers c
JOIN fact_customer_account f
    ON c.customer_id = f.customer_id
JOIN dim_contract dc
    ON f.contract_id = dc.contract_id
JOIN dim_payment dp
    ON f.payment_id = dp.payment_id
LIMIT 10;

"""

#65
#-------

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(20), primary_key=True)
    gender = Column(String(10))
    senior_citizen = Column(Integer, nullable=False)
    partner = Column(Integer, nullable=False)
    dependents = Column(Integer, nullable=False)

    account = relationship("CustomerAccount", back_populates="customer", uselist=False)

class Contract(Base):
    __tablename__ = "dim_contract"

    contract_id = Column(Integer, primary_key=True)
    contract_type = Column(String(30), unique=True, nullable=False)

    accounts = relationship("CustomerAccount", back_populates="contract")

class CustomerAccount(Base):
    __tablename__ = "fact_customer_account"

    customer_id = Column(
        String(20),
        ForeignKey("customers.customer_id"),
        primary_key=True
    )

    contract_id = Column(
        Integer,
        ForeignKey("dim_contract.contract_id"),
        nullable=False
    )

    payment_id = Column(
        Integer,
        ForeignKey("dim_payment.payment_id"),
        nullable=False
    )

    tenure = Column(Integer)
    monthly_charges = Column(Integer)
    total_charges = Column(Integer)
    churn = Column(Integer, nullable=False)

    customer = relationship("Customer", back_populates="account")
    contract = relationship("Contract", back_populates="accounts")

# 66
# -------

engine = create_engine(
    "mysql+pymysql://root:root@localhost:3306/customer_churn"
)

Session = sessionmaker(bind=engine)
session = Session()

customer = (
    session.query(Customer)
    .filter_by(customer_id="0004-TLHLJ")
    .first()
)

if customer:
    print(customer.customer_id)
    print(customer.gender)
    print(customer.partner)
    print(customer.dependents)