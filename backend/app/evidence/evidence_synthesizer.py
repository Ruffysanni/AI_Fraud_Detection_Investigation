
from typing import Any

from backend.app.evidence.evidence_collector import (
    collect_investigation_evidence,
)
from backend.app.evidence.evidence_validator import (
    validate_evidence_package,
)
from backend.app.evidence.evidence_classifier import (
    classify_evidence,
)
from backend.app.evidence.evidence_assessor import (
    assess_evidence_strength,
)


def synthesize_investigation_evidence(
    transaction_id: int,
) -> dict[str, Any]:
    """
    Collect, validate, classify, and assess investigation evidence
    into one consolidated evidence package.
    """

    # Step 1: Collect evidence
    package = collect_investigation_evidence(transaction_id)

    # Stop if collection failed
    if package.get("evidence_status") == "failed":
        return {
            "transaction_id": transaction_id,
            "synthesis_status": "failed",
            "error": "Evidence collection failed.",
            "evidence_package": package,
        }

    # Step 2: Validate evidence
    validation = validate_evidence_package(package)

    if not validation.get("valid"):
        return {
            "transaction_id": transaction_id,
            "synthesis_status": "failed",
            "error": "Evidence validation failed.",
            "validation": validation,
            "evidence_package": package,
        }

    # Step 3: Classify evidence
    classification = classify_evidence(package)

    # Step 4: Assess evidence
    assessment = assess_evidence_strength(classification)

    # Step 5: Consolidate everything
    return {
        "transaction_id": transaction_id,
        "synthesis_status": (
            "partial"
            if (
                package.get("evidence_status") == "partial"
                or validation.get("validation_status") == "partial"
            )
            else "completed"
        ),
        "validation": validation,
        "classification": classification,
        "assessment": assessment,
        "evidence_package": package,
        "synthesis_metadata": {
            "synthesis_version": "1.0",
            "components": [
                "evidence_collection",
                "evidence_validation",
                "evidence_classification",
                "evidence_strength_assessment",
            ],
        },
        "disclaimer": (
            "This consolidated package supports fraud investigation. "
            "It does not independently establish fraudulent activity."
        ),
    }
