
from typing import Any


def assess_evidence_strength(
    classified_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess evidence completeness, supporting observations,
    and investigation limitations.

    This function evaluates evidence availability and structure.
    It does not determine whether fraud actually occurred.
    """

    if not isinstance(classified_result, dict):
        raise ValueError("Classified evidence must be a dictionary.")

    if classified_result.get("classification_status") != "completed":
        raise ValueError("Evidence classification is not completed.")

    classified = classified_result.get("classified_evidence", {})

    required_categories = [
        "transaction_facts",
        "ml_assessment",
        "rule_based_observations",
        "comparable_transactions",
        "retrieved_guidance",
    ]

    available_categories = [
        category
        for category in required_categories
        if category in classified
    ]

    missing_categories = [
        category
        for category in required_categories
        if category not in classified
    ]

    limitations = []
    supporting_observations = []
    
    limitations.extend(
        classified_result.get("collection_limitations", [])
    )
    

    # 1. Transaction facts
    transaction_facts = classified.get("transaction_facts", {}).get("data", {})

    if transaction_facts:
        supporting_observations.append(
            "Transaction details were successfully retrieved from PostgreSQL."
        )
    else:
        limitations.append(
            "Transaction facts are unavailable."
        )

    # 2. Machine learning assessment
    ml_data = classified.get("ml_assessment", {}).get("data", {})
    risk_assessment = ml_data.get("risk_assessment", {})
    fraud_score = risk_assessment.get("fraud_score")

    if isinstance(fraud_score, (int, float)) and not isinstance(fraud_score, bool):
        if 0 <= fraud_score <= 1:
            if fraud_score >= 0.5:
                supporting_observations.append(
                    "The model estimated elevated fraud risk based on its configured threshold."
                )
            else:
                supporting_observations.append(
                    "The model estimated fraud risk below its configured threshold."
                )
        else:
            limitations.append(
                "The ML fraud score is outside the expected range."
            )
    else:
        limitations.append(
            "A valid ML fraud score is unavailable."
        )

    # 3. Rule-based observations
    rule_data = classified.get("rule_based_observations", {})
    observation_groups = rule_data.get("groups", [])

    observed_rules = []

    for group in observation_groups:
        for observation in group.get("observations", []):
            if observation.get("observed") is True:
                observed_rules.append(observation.get("indicator"))

    if observed_rules:
        supporting_observations.append(
            f"{len(observed_rules)} rule-based observations were identified."
        )
    else:
        limitations.append(
            "No positive rule-based observations were identified."
        )

    # 4. Comparable transactions
    comparable_data = classified.get("comparable_transactions", {})
    comparable_records = comparable_data.get("records", [])

    if comparable_records:
        supporting_observations.append(
            f"{len(comparable_records)} potentially comparable transaction(s) were found."
        )
    else:
        limitations.append(
            "No comparable transactions were found. Transaction comparison is limited."
        )

    # 5. Retrieved guidance
    guidance_data = classified.get("retrieved_guidance", {}).get("data", {})
    guidance_sources = guidance_data.get("sources", [])

    if guidance_sources:
        supporting_observations.append(
            f"{len(guidance_sources)} knowledge-base source reference(s) were retrieved."
        )
    else:
        limitations.append(
            "No investigation guidance was retrieved from the knowledge base."
        )

    # 6. Missing evidence categories
    if missing_categories:
        limitations.append(
            "Missing evidence categories: "
            + ", ".join(missing_categories)
        )

    # 7. Investigation caveats
    limitations.extend([
        "ML risk estimates do not independently establish fraudulent activity.",
        "Correlated balance observations must not be counted as independent confirmations.",
        "Comparable transactions are not confirmed to involve the same accounts.",
        "Retrieved knowledge-base guidance is illustrative and is not official banking policy.",
    ])

    # 8. Overall evidence assessment
    if missing_categories or not transaction_facts:
        overall_assessment = "incomplete"
    elif fraud_score is None or not isinstance(fraud_score, (int, float)) or isinstance(fraud_score, bool):
        overall_assessment = "incomplete"
    elif not observed_rules and not comparable_records:
        overall_assessment = "limited"
    else:
        overall_assessment = "available_for_manual_review"

    return {
        "transaction_id": classified_result.get("transaction_id"),
        "assessment_status": "completed",
        "evidence_completeness": {
            "required_categories": required_categories,
            "available_categories": available_categories,
            "missing_categories": missing_categories,
        },
        "supporting_observations": supporting_observations,
        "limitations": limitations,
        "overall_assessment": overall_assessment,
        "disclaimer": (
            "This assessment summarizes the availability and limitations "
            "of investigation evidence. It does not confirm fraud or replace "
            "manual investigation."
        ),
    }
