
from typing import Any


def classify_evidence(
    package: dict[str, Any],
) -> dict[str, Any]:
    """
    Organize validated investigation evidence by source
    and distinguish independent observations from
    correlated rule-based indicators.
    """

    transaction_id = package.get("transaction_id")

    transaction_facts = package.get("transaction_facts", {})
    ml_assessment = package.get("ml_assessment", {})
    observations = package.get("rule_based_observations", [])
    comparable_transactions = package.get(
        "comparable_transactions", []
    )
    retrieved_guidance = package.get("retrieved_guidance", {})

    # 1. Classify transaction facts.
    classified_transaction_facts = {
        "evidence_type": "transaction_facts",
        "source": "PostgreSQL transactions table",
        "data": transaction_facts,
    }

    # 2. Classify ML assessment.
    classified_ml_assessment = {
        "evidence_type": "machine_learning_assessment",
        "source": "Fraud detection model",
        "data": ml_assessment,
        "interpretation": (
            "Model-generated risk estimate. "
            "It does not independently establish fraud."
        ),
    }

    # 3. Group rule-based observations.
    balance_indicators = {
        "origin_balance_reduced_to_zero",
        "destination_balance_matches_amount",
        "origin_balance_reduction_matches_amount",
    }

    balance_observations = []
    other_observations = []

    for observation in observations:
        if observation.get("indicator") in balance_indicators:
            balance_observations.append(observation)
        else:
            other_observations.append(observation)

    classified_rule_observations = {
        "evidence_type": "rule_based_observations",
        "source": "Transaction anomaly analysis",
        "groups": [
            {
                "group": "balance_movement",
                "observations": balance_observations,
                "interpretation": (
                    "These observations describe related aspects "
                    "of the same transaction balance movement. "
                    "They should not be counted as independent "
                    "confirmations."
                ),
            },
            {
                "group": "other_transaction_patterns",
                "observations": other_observations,
                "interpretation": (
                    "Other rule-based observations requiring "
                    "contextual examination."
                ),
            },
        ],
    }

    # 4. Classify potentially comparable transactions.
    classified_comparable_transactions = {
        "evidence_type": "comparable_transactions",
        "source": "PostgreSQL transaction records",
        "records": comparable_transactions,
        "interpretation": (
            "Records selected using transaction type and amount "
            "similarity. They are not confirmed to involve "
            "the same accounts."
        ),
    }

    # 5. Classify retrieved investigation guidance.
    classified_guidance = {
        "evidence_type": "retrieved_investigation_guidance",
        "source": "Local RAG knowledge base",
        "data": retrieved_guidance,
        "interpretation": (
            "Reference guidance for investigation. "
            "It is not transaction-specific evidence and "
            "is not an official banking policy."
        ),
    }

    # 6. Assemble the classification package.
    return {
        "transaction_id": transaction_id,
        "classification_status": "completed",
            "collection_status": package.get("evidence_status"),
            "collection_limitations": package.get(
                "evidence_assessment", {}
            ).get("limitations", []),
        "classified_evidence": {
            "transaction_facts": classified_transaction_facts,
            "ml_assessment": classified_ml_assessment,
            "rule_based_observations": (
                classified_rule_observations
            ),
            "comparable_transactions": (
                classified_comparable_transactions
            ),
            "retrieved_guidance": classified_guidance,
        },
        "classification_notes": [
            "Transaction facts are separated from model estimates.",
            "Rule-based observations are not treated as proof of fraud.",
            "Correlated balance observations are grouped together.",
            "Comparable transactions are not assumed to share accounts.",
            "Retrieved guidance is reference material, not transaction evidence.",
        ],
    }
