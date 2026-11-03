from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from backend.app.evidence.evidence_synthesizer import (
    synthesize_investigation_evidence,
)
import json
from pathlib import Path


def create_report_structure(
    transaction_id: int,
) -> dict[str, Any]:
    """
    Create the initial structure for a fraud investigation report.
    """

    return {
        "report_metadata": {
            "report_id": str(uuid4()),
            "transaction_id": transaction_id,
            "report_type": "transaction_fraud_investigation",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "report_version": "1.0",
        },
        "investigation_summary": {},
        "transaction_details": {},
        "ml_assessment": {},
        "rule_based_observations": [],
        "comparable_transactions": [],
        "retrieved_guidance": [],
        "supporting_observations": [],
        "evidence_limitations": [],
        "overall_assessment": {},
        "recommended_actions": [],
        "disclaimer": (
            "This report is an investigative aid. "
            "A machine-learning risk estimate or anomaly observation "
            "does not independently confirm fraudulent activity. "
            "All findings require appropriate human review."
        ),
    }

def generate_investigation_report(
    transaction_id: int,
) -> dict[str, Any]:
    """
    Generate a structured investigation report from synthesized evidence.
    """

    # Step 1: Run the evidence synthesis pipeline.
    synthesis_result = synthesize_investigation_evidence(
        transaction_id
    )

    # Step 2: Create the initial report structure.
    report = create_report_structure(transaction_id)

    # Step 3: Extract the synthesis components safely.
    evidence_package = synthesis_result.get(
        "evidence_package", {}
    )
    classification = synthesis_result.get(
        "classification", {}
    )
    assessment = synthesis_result.get(
        "assessment", {}
    )

    classified_evidence = classification.get(
        "classified_evidence", {}
    )

    # Step 4: Update report metadata.
    report["report_metadata"].update({
        "synthesis_status": synthesis_result.get(
            "synthesis_status", "unknown"
        ),
        "evidence_status": evidence_package.get(
            "evidence_status", "unknown"
        ),
        "validation_status": synthesis_result.get(
            "validation", {}
        ).get("validation_status", "unknown"),
    })

    # Step 5: Populate the investigation summary.
    report["investigation_summary"] = {
        "transaction_id": transaction_id,
        "synthesis_status": synthesis_result.get(
            "synthesis_status", "unknown"
        ),
        "assessment_status": assessment.get(
            "assessment_status", "unknown"
        ),
        "evidence_completeness": assessment.get(
            "evidence_completeness", {}
        ),
    }

    # Step 6: Populate transaction and ML details.
    report["transaction_details"] = evidence_package.get(
        "transaction_facts", {}
    )

    ml_evidence = evidence_package.get(
        "ml_assessment", {}
    )

    report["ml_assessment"] = {
        "risk_assessment": ml_evidence.get(
            "risk_assessment", {}
        ),
        "alerts": ml_evidence.get("alerts", []),
        "disclaimer": ml_evidence.get("disclaimer"),
    }

    # Step 7: Populate the classified evidence sections.
    report["rule_based_observations"] = (
        classified_evidence.get(
            "rule_based_observations", {}
        ).get("groups", [])
    )

    report["comparable_transactions"] = (
        classified_evidence.get(
            "comparable_transactions", {}
        ).get("records", [])
    )

    report["retrieved_guidance"] = (
        classified_evidence.get(
            "retrieved_guidance", {}
        ).get("data", {}).get("sources", [])
    )

    # Step 8: Populate the evidence assessment.
    report["supporting_observations"] = (
        assessment.get("supporting_observations", [])
    )

    # Preserve limitations from both evidence collection and assessment.
    collection_limitations = evidence_package.get(
        "evidence_assessment", {}
    ).get("limitations", [])

    assessment_limitations = assessment.get(
        "limitations", []
    )

    report["evidence_limitations"] = list(dict.fromkeys(
        collection_limitations + assessment_limitations
    ))

    report["overall_assessment"] = {
        "result": assessment.get("overall_assessment"),
        "validation_status": synthesis_result.get(
            "validation", {}
        ).get("validation_status", "unknown"),
        "synthesis_status": synthesis_result.get(
            "synthesis_status", "unknown"
        ),
    }

    # Step 9: Generate evidence-based recommendations.
    recommendations = []
    
    # Handle missing transaction details first.
    if not report["transaction_details"]:
        recommendations.append(
            "Verify the transaction ID and confirm that the "
            "transaction exists in the database before proceeding."
        )

        recommendations.append(
            "Retry evidence collection after valid transaction "
            "details have been retrieved."
        )

        report["recommended_actions"] = recommendations
        return report

    # Check the overall evidence synthesis status.
    if synthesis_result.get("synthesis_status") != "completed":
        recommendations.append(
            "Review the incomplete evidence and resolve "
            "the identified collection or validation issues."
        )

    # Check the ML risk level.
    risk_assessment = ml_evidence.get("risk_assessment", {})
    risk_level = risk_assessment.get("risk_level")

    if risk_level == "high":
        recommendations.append(
            "Prioritize manual investigation of this transaction "
            "because the model assigned a high-risk estimate."
        )
    elif risk_level == "medium":
        recommendations.append(
            "Review the transaction and its supporting evidence "
            "because the model assigned a medium-risk estimate."
        )
    elif not risk_assessment:
        recommendations.append(
            "Obtain or verify the machine-learning risk assessment."
        )

    # Examine rule-based observations.
    rule_groups = report["rule_based_observations"]

    balance_group = next(
        (
            group for group in rule_groups
            if group.get("group") == "balance_movement"
        ),
        None,
    )

    if balance_group:
        recommendations.append(
            "Review the origin and destination balance movements "
            "against available transaction records. Treat correlated "
            "balance indicators as related observations, not "
            "independent confirmations."
        )

    # Examine comparable transaction records.
    if report["comparable_transactions"]:
        recommendations.append(
            "Compare the potentially similar transactions using "
            "additional account-level information. Similarity in "
            "amount and transaction type does not establish "
            "a relationship between accounts."
        )
    else:
        recommendations.append(
            "Obtain additional transaction context because no "
            "potentially comparable transactions were retrieved."
        )

    # Check retrieved investigation guidance.
    if not report["retrieved_guidance"]:
        recommendations.append(
            "Consult relevant investigation procedures because "
            "no knowledge-base guidance was retrieved."
        )

    # Include a general human-review recommendation.
    recommendations.append(
        "Have an authorized investigator review the available "
        "evidence before reaching a fraud determination."
    )

    report["recommended_actions"] = recommendations

    return report

def export_report_to_json(
    report: dict[str, Any],
    output_dir: str = "data/reports",
) -> str:
    """
    Export a generated investigation report as a JSON file.
    """

    if not isinstance(report, dict):
        raise TypeError("Report must be a dictionary.")

    metadata = report.get("report_metadata", {})

    transaction_id = metadata.get("transaction_id")
    report_id = metadata.get("report_id")

    if transaction_id is None or not report_id:
        raise ValueError(
            "Report must contain a transaction ID and report ID."
        )

    # Create the output directory if it does not exist.
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename.
    filename = f"transaction_{transaction_id}_{report_id}.json"
    file_path = directory / filename

    # Write the report to JSON.
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            default=str,
        )

    return str(file_path)


def generate_and_export_report(
    transaction_id: int,
    output_dir: str = "data/reports",
) -> dict[str, Any]:
    """
    Generate an investigation report and export it as JSON.
    """

    report = generate_investigation_report(transaction_id)

    file_path = export_report_to_json(
        report,
        output_dir,
    )

    return {
        "success": True,
        "transaction_id": transaction_id,
        "report_id": report["report_metadata"]["report_id"],
        "file_path": file_path,
        "synthesis_status": report["report_metadata"][
            "synthesis_status"
        ],
    }