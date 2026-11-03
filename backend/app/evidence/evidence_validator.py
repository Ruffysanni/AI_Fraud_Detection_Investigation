
from typing import Any


def validate_evidence_package(
    package: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the structure and completeness of a
    transaction investigation evidence package.
    """

    errors = []
    warnings = []
    validated_sections = []

    # 1. Validate the evidence package itself.
    if not isinstance(package, dict):
        return {
            "valid": False,
            "validation_status": "failed",
            "errors": ["Evidence package must be a dictionary."],
            "warnings": [],
            "validated_sections": [],
        }

    # 2. Validate transaction ID.
    transaction_id = package.get("transaction_id")

    if not isinstance(transaction_id, int) or isinstance(
        transaction_id, bool
    ) or transaction_id <= 0:
        errors.append("A valid positive transaction ID is required.")
    else:
        validated_sections.append("transaction_id")

    # 3. Validate transaction facts.
    transaction = package.get("transaction_facts")

    required_transaction_fields = [
        "transaction_id",
        "step",
        "transaction_type",
        "amount",
        "oldbalance_org",
        "newbalance_orig",
        "oldbalance_dest",
        "newbalance_dest",
    ]

    if not isinstance(transaction, dict) or not transaction:
        errors.append("Transaction facts are missing.")
    else:
        missing_fields = [
            field
            for field in required_transaction_fields
            if field not in transaction
        ]

        if missing_fields:
            errors.append(
                "Transaction facts are missing fields: "
                + ", ".join(missing_fields)
            )
        elif transaction.get("transaction_id") != transaction_id:
            errors.append(
                "Transaction ID does not match the evidence package."
            )
        else:
            validated_sections.append("transaction_facts")

    # 4. Validate ML assessment.
    ml_assessment = package.get("ml_assessment")

    if not isinstance(ml_assessment, dict) or not ml_assessment:
        warnings.append("ML assessment is unavailable.")
    else:
        risk = ml_assessment.get("risk_assessment", {})

        if not isinstance(risk, dict) or not risk:
            warnings.append("ML risk assessment details are missing.")
        else:
            required_ml_fields = [
                "transaction_id",
                "fraud_score",
                "prediction",
                "prediction_label",
                "risk_level",
                "threshold",
            ]

            missing_ml_fields = [
                field
                for field in required_ml_fields
                if field not in risk
            ]

            if missing_ml_fields:
                warnings.append(
                    "ML assessment is missing fields: "
                    + ", ".join(missing_ml_fields)
                )
            elif risk.get("transaction_id") != transaction_id:
                errors.append(
                    "ML assessment transaction ID does not match."
                )
            else:
                score = risk.get("fraud_score")

                if (
                    not isinstance(score, (int, float))
                    or isinstance(score, bool)
                    or not 0 <= score <= 1
                ):
                    errors.append(
                        "ML fraud score must be between 0 and 1."
                    )
                else:
                    validated_sections.append("ml_assessment")

    # 5. Validate rule-based observations.
    observations = package.get("rule_based_observations")

    if not isinstance(observations, list):
        errors.append(
            "Rule-based observations must be a list."
        )
    else:
        invalid_observations = [
            item
            for item in observations
            if not isinstance(item, dict)
            or not isinstance(item.get("indicator"), str)
            or not isinstance(item.get("description"), str)
            or not isinstance(item.get("observed"), bool)
        ]

        if invalid_observations:
            errors.append(
                "One or more rule-based observations have an invalid structure."
            )
        elif not observations:
            warnings.append("No rule-based observations were collected.")
        else:
            validated_sections.append("rule_based_observations")

    # 6. Validate comparable transactions.
    comparable = package.get("comparable_transactions")

    if not isinstance(comparable, list):
        errors.append(
            "Comparable transactions must be a list."
        )
    else:
        invalid_comparables = [
            item
            for item in comparable
            if not isinstance(item, dict)
            or "transaction_id" not in item
            or "transaction_type" not in item
            or "amount" not in item
        ]

        if invalid_comparables:
            errors.append(
                "One or more comparable transaction records are invalid."
            )
        else:
            validated_sections.append("comparable_transactions")

            if not comparable:
                warnings.append(
                    "No potentially comparable transactions were found."
                )

    # 7. Validate retrieved guidance.
    guidance = package.get("retrieved_guidance")

    if not isinstance(guidance, dict) or not guidance:
        warnings.append("Retrieved investigation guidance is unavailable.")
    else:
        sources = guidance.get("sources")

        if not isinstance(sources, list):
            errors.append(
                "Retrieved guidance sources must be a list."
            )
        else:
            invalid_sources = [
                source
                for source in sources
                if not isinstance(source, dict)
                or not source.get("filename")
                or not source.get("source")
                or not source.get("chunk_id")
            ]

            if invalid_sources:
                errors.append(
                    "One or more retrieved source references are invalid."
                )
            else:
                validated_sections.append("retrieved_guidance")

                if not sources:
                    warnings.append(
                        "No relevant guidance sources were retrieved."
                    )

    # 8. Determine validation status.
    if errors:
        validation_status = "failed"
    elif warnings:
        validation_status = "partial"
    else:
        validation_status = "passed"

    return {
        "valid": len(errors) == 0,
        "validation_status": validation_status,
        "transaction_id": transaction_id,
        "validated_sections": validated_sections,
        "errors": errors,
        "warnings": warnings,
    }
