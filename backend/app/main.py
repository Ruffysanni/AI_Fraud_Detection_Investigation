
"""API for transaction fraud detection and investigation."""

from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.database import get_db_connection
from backend.app.reports.report_generator import (
    generate_investigation_report,
    export_report_to_json,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BACKEND_DIR / "models" / "fraud_model.joblib"

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Trained model not found: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

app = FastAPI(
    title="Fraud Detection and Investigation API",
    description="API for transaction fraud detection and investigation.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class TransactionInput(BaseModel):
    """Validate the transaction fields required by the model."""

    step: int = Field(ge=0)
    type: Literal[
        "CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"
    ]
    amount: float = Field(ge=0)
    oldbalanceOrg: float = Field(ge=0)
    newbalanceOrig: float = Field(ge=0)
    oldbalanceDest: float = Field(ge=0)
    newbalanceDest: float = Field(ge=0)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "The API is running successfully.",
    }
    

@app.get("/dashboard/metrics")
def get_dashboard_metrics():
    """Return live dashboard statistics from PostgreSQL."""

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        (SELECT COUNT(*)
                         FROM transactions)
                            AS transactions_analyzed,

                        (SELECT COUNT(*)
                         FROM transactions
                         WHERE prediction = 1)
                            AS flagged_transactions,

                        (SELECT COUNT(*)
                         FROM investigation_alerts
                         WHERE status = 'open')
                            AS open_investigations,

                        (SELECT COUNT(*)
                         FROM investigation_alerts
                         WHERE severity = 'high')
                            AS high_risk_alerts
                    """
                )

                row = cur.fetchone()

        return {
            "transactions_analyzed": row[0],
            "flagged_transactions": row[1],
            "open_investigations": row[2],
            "high_risk_alerts": row[3],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve dashboard metrics.",
        ) from exc



@app.post("/predict")
def predict_fraud(transaction: TransactionInput):
    """Score, save, and optionally alert on a transaction."""

    features = pd.DataFrame([{
        "step": transaction.step,
        "type": transaction.type,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "newbalanceOrig": transaction.newbalanceOrig,
        "oldbalanceDest": transaction.oldbalanceDest,
        "newbalanceDest": transaction.newbalanceDest,
    }])

    try:
        fraud_score = float(model.predict_proba(features)[0][1])
        prediction = int(fraud_score >= 0.5)

        if fraud_score >= 0.7:
            risk_level = "high"
        elif fraud_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        prediction_label = (
            "fraud_suspected"
            if prediction == 1
            else "legitimate_predicted"
        )

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO transactions (
                        step, transaction_type, amount,
                        oldbalance_org, newbalance_orig,
                        oldbalance_dest, newbalance_dest,
                        fraud_score, prediction, prediction_label,
                        risk_level, threshold
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                    RETURNING transaction_id
                    """,
                    (
                        transaction.step,
                        transaction.type,
                        transaction.amount,
                        transaction.oldbalanceOrg,
                        transaction.newbalanceOrig,
                        transaction.oldbalanceDest,
                        transaction.newbalanceDest,
                        fraud_score,
                        prediction,
                        prediction_label,
                        risk_level,
                        0.5,
                    ),
                )

                transaction_id = cur.fetchone()[0]
                alert_id = None

                # Medium- and high-risk assessments need review.
                if risk_level in ("medium", "high"):
                    reason = (
                        f"The model assigned {risk_level} risk "
                        f"(fraud score: {fraud_score:.4f}). "
                        "Manual investigation is recommended."
                    )

                    cur.execute(
                        """
                        INSERT INTO investigation_alerts (
                            transaction_id, severity, reason
                        )
                        VALUES (%s, %s, %s)
                        RETURNING alert_id
                        """,
                        (transaction_id, risk_level, reason),
                    )
                    alert_id = cur.fetchone()[0]

        return {
            "transaction_id": transaction_id,
            "prediction": prediction,
            "prediction_label": prediction_label,
            "fraud_score": round(fraud_score, 4),
            "risk_level": risk_level,
            "threshold": 0.5,
            "alert_created": alert_id is not None,
            "alert_id": alert_id,
            "disclaimer": (
                "This is a model estimate for investigation support, "
                "not confirmation of fraud."
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to score and save this transaction.",
        ) from exc


@app.get("/transactions")
def get_transactions(
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return the most recently assessed transactions."""

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        transaction_id, step, transaction_type, amount,
                        fraud_score, prediction, prediction_label,
                        risk_level, created_at
                    FROM transactions
                    ORDER BY created_at DESC, transaction_id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()

        return [
            {
                "transaction_id": row[0],
                "step": row[1],
                "type": row[2],
                "amount": float(row[3]),
                "fraud_score": row[4],
                "prediction": row[5],
                "prediction_label": row[6],
                "risk_level": row[7],
                "created_at": row[8],
            }
            for row in rows
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve transaction history.",
        ) from exc


@app.get("/alerts")
def get_alerts(
    status: Literal["open", "reviewed", "closed"] | None = None,
    limit: int = Query(default=20, ge=1, le=100),
):
    """Return investigation alerts, optionally filtered by status."""

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if status is None:
                    cur.execute(
                        """
                        SELECT
                            a.alert_id, a.transaction_id, a.severity,
                            a.reason, a.status, a.created_at,
                            t.amount, t.fraud_score
                        FROM investigation_alerts AS a
                        JOIN transactions AS t
                            ON t.transaction_id = a.transaction_id
                        ORDER BY a.created_at DESC, a.alert_id DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT
                            a.alert_id, a.transaction_id, a.severity,
                            a.reason, a.status, a.created_at,
                            t.amount, t.fraud_score
                        FROM investigation_alerts AS a
                        JOIN transactions AS t
                            ON t.transaction_id = a.transaction_id
                        WHERE a.status = %s
                        ORDER BY a.created_at DESC, a.alert_id DESC
                        LIMIT %s
                        """,
                        (status, limit),
                    )

                rows = cur.fetchall()

        return [
            {
                "alert_id": row[0],
                "transaction_id": row[1],
                "severity": row[2],
                "reason": row[3],
                "status": row[4],
                "created_at": row[5],
                "amount": float(row[6]),
                "fraud_score": row[7],
            }
            for row in rows
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve investigation alerts.",
        ) from exc

@app.post("/reports/{transaction_id}/generate")
def generate_transaction_report(transaction_id: int):
    """Generate and export an investigation report."""

    if transaction_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transaction ID must be a positive integer.",
        )

    try:
        # Generate the investigation report.
        report = generate_investigation_report(transaction_id)

        # Confirm that transaction details were retrieved.
        if not report.get("transaction_details"):
            raise HTTPException(
                status_code=404,
                detail="Transaction not found. Report could not be generated.",
            )

        # Export the report to JSON.
        file_path = export_report_to_json(report)

        return {
            "success": True,
            "transaction_id": transaction_id,
            "report_id": report["report_metadata"]["report_id"],
            "synthesis_status": (
                report["report_metadata"]["synthesis_status"]
            ),
            "exported_file": file_path,
            "report": report,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate the investigation report.",
        ) from exc