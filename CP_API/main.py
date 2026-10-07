import logging
import os
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from services import get_churn_summary, get_high_risk_customers, get_customer_features
from fastapi.middleware.cors import CORSMiddleware
from ml4_predict import predict_churn

DATABASE_URL = "mysql+pymysql://root:root@localhost/customer_churn"
API_KEY = os.getenv("API_KEY")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class CustomerResponse(BaseModel):
    customer_id: str
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float
    churn: int

class HighRiskCustomerResponse(BaseModel):
    customer_id: str
    tenure: int
    monthly_charges: float
    contract_type: str
    risk_reason: str

class CustomerFeaturesRequest(BaseModel):
    customer_id: str
    service_count: int
    tenure_bucket: str
    high_charge_flag: bool
    is_long_term_customer: bool
    has_streaming_bundle: bool
    auto_pay_flag: bool
    monthly_charges: float
    total_charges: float

class ChurnPredictionRequest(BaseModel):
    tenure: int = Field(..., ge=0, lt=100)
    monthly_charges: float = Field(..., ge=0)
    contract_type: str
    service_count: int
    internet_service: str
    customer_id: str | None = None

class ErrorResponse(BaseModel):
    detail: str
    status_code: int

app = FastAPI()
API_KEY = os.getenv("API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")

    if api_key != API_KEY:
        logger.warning(
            "%s %s - 401",
            request.method,
            request.url.path
        )

        return JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid or missing API key",
                "status_code": 401
            }
        )

    response = await call_next(request)

    logger.info(
        "%s %s - %s",
        request.method,
        request.url.path,
        response.status_code
    )

    return response

@app.get("/customer/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str):
    session = SessionLocal()

    try:
        query = text("""
            SELECT
                c.customer_id,
                f.tenure,
                dc.contract_type,
                c.internet_service,
                f.monthly_charges,
                f.churn
            FROM customers c
            JOIN fact_customer_account f
                ON c.customer_id = f.customer_id
            JOIN dim_contract dc
                ON f.contract_id = dc.contract_id
            WHERE c.customer_id = :customer_id;
        """)

        result = session.execute(
            query,
            {"customer_id": customer_id}
        ).mappings().first()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} not found"
            )

        return CustomerResponse(**result)
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Database error while fetching customer {customer_id}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        session.close()

@app.get("/churn/summary")
def get_summary():
    session = SessionLocal()

    try:
        return get_churn_summary(session)
    except Exception:
        logger.exception("Database error while generating churn summary")

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )
    finally:
        session.close()

@app.get(
    "/customers/high-risk",
    response_model=list[HighRiskCustomerResponse]
)
def get_risk_customers(
    limit: int = Query(50, ge=1, le=500),
    min_tenure: int | None = Query(None, ge=0),
    max_tenure: int | None = Query(None, ge=0)
):
    session = SessionLocal()
    try:
        result = get_high_risk_customers(session, limit, min_tenure, max_tenure)
        return [
            HighRiskCustomerResponse(**row)
            for row in result
        ]

    except Exception:
        logger.exception("Database error while fetching high-risk customers")
        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )
    finally:
        session.close()

@app.get("/customer/{customer_id}/features")
def get_customerfeatures(customer_id: str):
    session = SessionLocal()

    try:
        result = get_customer_features(session, customer_id)
        if result is None:
            logger.warning(f"Customer features for {customer_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} not found"
            )
        return CustomerFeaturesRequest(**result)
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Database error while fetching customer features for {customer_id}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        session.close()

@app.post("/predict-churn")
def predict_customer_churn(request: ChurnPredictionRequest):
    try:
        result = predict_churn(
            request.tenure,
            request.monthly_charges,
            request.contract_type,
            request.service_count,
            request.internet_service
        )

        return result

    except Exception:
        logger.exception("Prediction failed")

        raise HTTPException(
            status_code=500,
            detail="Prediction failed"
        )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.warning(
        "%s %s - 404",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "status_code": 404
        }
    )