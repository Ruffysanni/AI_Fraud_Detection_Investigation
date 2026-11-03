from typing import Any

from backend.app.agents.investigation_tools import (
    get_transaction_details,
    get_fraud_risk_score,
    analyze_transaction_anomalies,
    get_related_transactions,
    search_fraud_policies,
)

from backend.app.evidence.evidence_schema import (
    create_evidence_package,
)


def collect_investigation_evidence(
    transaction_id: int,
    policy_query: str = (
        "What transaction patterns and balance movements "
        "may indicate suspicious movement of funds?"
    ),
) -> dict[str, Any]:
    """
    Collect evidence from the investigation tools
    and organize it into a standardized evidence package.
    """

    package = create_evidence_package(transaction_id)

    
    tool_results = {}

    # 1. Retrieve transaction details first.
    try:
        transaction_result = get_transaction_details(transaction_id)
    except Exception as error:
        transaction_result = {
            "success": False,
            "message": str(error),
        }

    tool_results["transaction_details"] = transaction_result

    # Stop immediately if the transaction cannot be retrieved.
    if not transaction_result.get("success"):
        package["evidence_status"] = "failed"
        package["evidence_assessment"]["limitations"].append(
            "Transaction details could not be retrieved. "
            "Evidence collection was stopped."
        )
        package["tool_results"] = tool_results

        return package

    # 2. Collect the remaining evidence only after
    # successful transaction retrieval.
    tools = {
        "ml_assessment": lambda: get_fraud_risk_score(
            transaction_id
        ),
        "anomaly_analysis": lambda: analyze_transaction_anomalies(
            transaction_id
        ),
        "comparable_transactions": lambda: get_related_transactions(
            transaction_id
        ),
        "retrieved_guidance": lambda: search_fraud_policies(
            policy_query
        ),
    }

    for tool_name, tool_function in tools.items():
        try:
            tool_results[tool_name] = tool_function()
        except Exception as error:
            tool_results[tool_name] = {
                "success": False,
                "message": str(error),
            }


    # 2. Populate transaction facts
    package["transaction_facts"] = transaction_result.get(
        "transaction", {}
    )

    # 3. Populate ML assessment
    risk_result = tool_results["ml_assessment"]

    if risk_result.get("success"):
        package["ml_assessment"] = {
            "risk_assessment": risk_result.get(
                "risk_assessment", {}
            ),
            "alerts": risk_result.get("alerts", []),
            "disclaimer": risk_result.get("disclaimer"),
        }

    # 4. Populate rule-based observations
    anomaly_result = tool_results["anomaly_analysis"]

    if anomaly_result.get("success"):
        package["rule_based_observations"] = (
            anomaly_result.get("indicators", [])
        )

    # 5. Populate potentially comparable transactions
    related_result = tool_results["comparable_transactions"]

    if related_result.get("success"):
        package["comparable_transactions"] = (
            related_result.get(
                "potentially_comparable_transactions", []
            )
        )

    # 6. Populate retrieved guidance
    guidance_result = tool_results["retrieved_guidance"]

    if guidance_result.get("success"):
        package["retrieved_guidance"] = {
            "query": guidance_result.get("query"),
            "results_count": guidance_result.get(
                "results_count", 0
            ),
            "knowledge_base_chunks": guidance_result.get(
                "knowledge_base_chunks", []
            ),
            "sources": guidance_result.get("sources", []),
            "disclaimer": guidance_result.get("disclaimer"),
        }

        package["sources"] = guidance_result.get("sources", [])

    # 7. Record unsuccessful tool calls
    failed_tools = [
        name
        for name, result in tool_results.items()
        if not result.get("success")
    ]

    for tool_name in failed_tools:
        package["evidence_assessment"]["limitations"].append(
            f"Evidence from {tool_name} could not be collected: "
            f"{tool_results[tool_name].get('message', 'Unknown error')}"
        )

    # 8. Determine collection status
    package["evidence_status"] = (
        "partial" if failed_tools else "completed"
    )

    # Keep original tool responses for traceability and debugging.
    package["tool_results"] = tool_results

    return package