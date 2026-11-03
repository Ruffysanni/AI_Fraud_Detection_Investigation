from psycopg.types.json import Jsonb
from backend.app.rag.retrieval import RAGRetriever
from typing import Any

from backend.app.database import get_db_connection


def get_transaction_details(transaction_id: int) -> dict[str, Any]:
    """
    Retrieve the complete details of a transaction.
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    transaction_id,
                    step,
                    transaction_type,
                    amount,
                    oldbalance_org,
                    newbalance_orig,
                    oldbalance_dest,
                    newbalance_dest,
                    created_at
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )

            row = cur.fetchone()

    if row is None:
        return {
            "success": False,
            "message": "Transaction not found.",
            "transaction_id": transaction_id,
        }

    return {
        "success": True,
        "transaction": {
            "transaction_id": row[0],
            "step": row[1],
            "transaction_type": row[2],
            "amount": float(row[3]),
            "oldbalance_org": float(row[4]),
            "newbalance_orig": float(row[5]),
            "oldbalance_dest": float(row[6]),
            "newbalance_dest": float(row[7]),
            "created_at": row[8].isoformat(),
        },
    }


def get_fraud_risk_score(transaction_id: int) -> dict[str, Any]:
    """
    Retrieve the ML fraud assessment and associated alerts.
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    transaction_id,
                    fraud_score,
                    prediction,
                    prediction_label,
                    risk_level,
                    threshold
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )

            row = cur.fetchone()

            if row is None:
                return {
                    "success": False,
                    "message": "Transaction not found.",
                    "transaction_id": transaction_id,
                }

            cur.execute(
                """
                SELECT
                    alert_id,
                    severity,
                    reason,
                    status,
                    created_at
                FROM investigation_alerts
                WHERE transaction_id = %s
                ORDER BY created_at DESC, alert_id DESC
                """,
                (transaction_id,),
            )

            alert_rows = cur.fetchall()

    alerts = [
        {
            "alert_id": alert[0],
            "severity": alert[1],
            "reason": alert[2],
            "status": alert[3],
            "created_at": alert[4].isoformat(),
        }
        for alert in alert_rows
    ]

    return {
        "success": True,
        "risk_assessment": {
            "transaction_id": row[0],
            "fraud_score": row[1],
            "prediction": row[2],
            "prediction_label": row[3],
            "risk_level": row[4],
            "threshold": row[5],
        },
        "alerts": alerts,
        "disclaimer": (
            "The ML risk score is an estimate for investigation "
            "support and does not confirm fraudulent activity."
        ),
    }


def analyze_transaction_anomalies(
    transaction_id: int,
) -> dict[str, Any]:
    """
    Identify rule-based transaction characteristics
    that may warrant further investigation.

    This analysis is separate from the ML risk score.
    """

    transaction_result = get_transaction_details(transaction_id)

    if not transaction_result["success"]:
        return transaction_result

    transaction = transaction_result["transaction"]

    amount = transaction["amount"]
    old_origin = transaction["oldbalance_org"]
    new_origin = transaction["newbalance_orig"]
    old_destination = transaction["oldbalance_dest"]
    new_destination = transaction["newbalance_dest"]
    transaction_type = transaction["transaction_type"]

    indicators = []

    # Check whether the origin account balance falls to zero.
    if old_origin > 0 and new_origin == 0:
        indicators.append({
            "indicator": "origin_balance_reduced_to_zero",
            "description": (
                "The origin account balance fell to zero "
                "after the transaction."
            ),
            "observed": True,
        })

    # Check whether the destination balance increases
    # by the transaction amount.
    if amount > 0 and abs(
        (new_destination - old_destination) - amount
    ) < 0.01:
        indicators.append({
            "indicator": "destination_balance_matches_amount",
            "description": (
                "The destination balance increased by "
                "approximately the transaction amount."
            ),
            "observed": True,
        })

    # Check whether the origin balance reduction matches
    # the transaction amount.
    if amount > 0 and abs(
        (old_origin - new_origin) - amount
    ) < 0.01:
        indicators.append({
            "indicator": "origin_balance_reduction_matches_amount",
            "description": (
                "The origin balance reduction matches "
                "approximately the transaction amount."
            ),
            "observed": True,
        })

    # Record the transaction type as contextual information.
    if transaction_type == "TRANSFER":
        indicators.append({
            "indicator": "transfer_transaction",
            "description": (
                "The transaction is a transfer and may warrant "
                "examination alongside related transaction activity."
            ),
            "observed": True,
        })

    return {
        "success": True,
        "transaction_id": transaction_id,
        "indicators_found": len(indicators),
        "indicators": indicators,
        "analysis_note": (
            "These are rule-based observations. They do not "
            "independently establish fraudulent activity."
        ),
    }


def search_fraud_policies(
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Search the fraud investigation knowledge base
    and return relevant guidance with source references.
    """

    retriever = RAGRetriever()

    try:
        total_chunks = retriever.build_index()

        results = retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        return {
            "success": True,
            "knowledge_base_chunks": total_chunks,
            "query": results["query"],
            "results_count": results["results_count"],
            "retrieved_context": results["retrieved_context"],
            "sources": results["sources"],
            "disclaimer": (
                "Retrieved content is illustrative prototype "
                "guidance, not an official banking policy "
                "or regulatory standard."
            ),
        }

    except (ValueError, RuntimeError) as exc:
        return {
            "success": False,
            "message": str(exc),
        }


def get_related_transactions(
    transaction_id: int,
    amount_tolerance: float = 0.10,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Find potentially comparable transactions using
    transaction type and amount similarity.

    These are not confirmed account-related transactions
    because account identifiers are not currently stored.
    """

    if not 0 <= amount_tolerance <= 1:
        return {
            "success": False,
            "message": "amount_tolerance must be between 0 and 1.",
        }

    if limit < 1 or limit > 20:
        return {
            "success": False,
            "message": "limit must be between 1 and 20.",
        }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    transaction_id,
                    transaction_type,
                    amount
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )

            target = cur.fetchone()

            if target is None:
                return {
                    "success": False,
                    "message": "Transaction not found.",
                    "transaction_id": transaction_id,
                }

            target_type = target[1]
            target_amount = float(target[2])

            minimum_amount = target_amount * (1 - amount_tolerance)
            maximum_amount = target_amount * (1 + amount_tolerance)

            cur.execute(
                """
                SELECT
                    transaction_id,
                    step,
                    transaction_type,
                    amount,
                    fraud_score,
                    risk_level,
                    created_at
                FROM transactions
                WHERE transaction_id != %s
                  AND transaction_type = %s
                  AND amount BETWEEN %s AND %s
                ORDER BY ABS(amount - %s), created_at DESC
                LIMIT %s
                """,
                (
                    transaction_id,
                    target_type,
                    minimum_amount,
                    maximum_amount,
                    target_amount,
                    limit,
                ),
            )

            rows = cur.fetchall()

    matches = [
        {
            "transaction_id": row[0],
            "step": row[1],
            "transaction_type": row[2],
            "amount": float(row[3]),
            "fraud_score": row[4],
            "risk_level": row[5],
            "created_at": row[6].isoformat(),
        }
        for row in rows
    ]

    return {
        "success": True,
        "reference_transaction_id": transaction_id,
        "matching_criteria": {
            "transaction_type": target_type,
            "minimum_amount": round(minimum_amount, 2),
            "maximum_amount": round(maximum_amount, 2),
        },
        "matches_found": len(matches),
        "potentially_comparable_transactions": matches,
        "limitation": (
            "Matches are based on transaction type and amount only. "
            "They are not confirmed to involve the same accounts."
        ),
    }

def save_investigation_findings(
    transaction_id: int,
    findings: dict[str, Any],
) -> dict[str, Any]:
    """
    Save structured investigation findings for a transaction.
    """

    if not isinstance(findings, dict) or not findings:
        return {
            "success": False,
            "message": "Findings must be a non-empty dictionary.",
        }

    with get_db_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT transaction_id
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )

            transaction = cur.fetchone()

            if transaction is None:
                return {
                    "success": False,
                    "message": "Transaction not found.",
                    "transaction_id": transaction_id,
                }

            cur.execute(
                """
                INSERT INTO investigation_findings (
                    transaction_id,
                    findings
                )
                VALUES (%s, %s)
                RETURNING finding_id, created_at
                """,
                (transaction_id, Jsonb(findings)),
            )

            saved_finding = cur.fetchone()

    return {
        "success": True,
        "message": "Investigation findings saved successfully.",
        "finding_id": saved_finding[0],
        "transaction_id": transaction_id,
        "created_at": saved_finding[1].isoformat(),
        "findings": findings,
    }