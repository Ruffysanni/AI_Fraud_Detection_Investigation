from typing import Any


def create_evidence_package(
    transaction_id: int,
) -> dict[str, Any]:
    """
    Create the standard structure for a transaction
    investigation evidence package.
    """

    return {
        "transaction_id": transaction_id,

        "evidence_status": "pending",

        "investigation_metadata": {
            "investigation_type": "transaction_fraud_investigation",
            "synthesis_version": "1.0",
        },

        "transaction_facts": {},

        "ml_assessment": {},

        "rule_based_observations": [],

        "comparable_transactions": [],

        "retrieved_guidance": [],

        "evidence_assessment": {
            "supporting_observations": [],
            "limitations": [],
            "overall_assessment": None,
        },

        "sources": [],
    }