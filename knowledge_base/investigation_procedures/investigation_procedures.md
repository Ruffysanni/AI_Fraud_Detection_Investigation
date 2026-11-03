# Fraud Investigation Procedures

**Document type:** Illustrative investigation procedure  
**Document ID:** IP-001  
**Version:** 1.0  
**Status:** Prototype knowledge-base document

## 1. Purpose

This document describes a structured approach to examining transactions flagged for potential fraudulent activity.

The procedure supports consistent evidence collection, analysis, documentation and escalation.

## 2. Initial Transaction Review

When a transaction is flagged for investigation:

1. Retrieve the transaction record from the transaction database.
2. Verify the transaction identifier and available transaction fields.
3. Review the transaction type and amount.
4. Examine the origin and destination account balance information, where available.
5. Retrieve the associated fraud risk score and model prediction.
6. Identify any existing alerts associated with the transaction.

The initial review should establish what information is available before drawing conclusions.

## 3. Transaction Pattern Analysis

Examine the transaction in the context of other available activity.

Consider:

- Previous transactions involving the origin account.
- Previous transactions involving the destination account.
- Similar transactions occurring around the same time.
- Repeated transactions involving the same accounts.
- Unusual changes in transaction amounts or frequency.

Where related transaction records are unavailable, document that limitation.

## 4. Evidence Collection

Collect relevant information from available sources.

Examples include:

- Transaction details retrieved from the database.
- Associated alert records.
- Machine learning risk scores and model version.
- Related transaction records.
- Relevant fraud indicator guidance retrieved from the knowledge base.

For each item, record its source and distinguish retrieved facts from analytical interpretations.

## 5. Evidence Validation

Before producing an investigation report:

1. Confirm that transaction identifiers match across retrieved records.
2. Verify that amounts and balances are taken directly from available records.
3. Confirm that model scores are associated with the correct transaction.
4. Check that referenced alerts actually exist.
5. Identify missing, inconsistent or unavailable information.
6. Avoid treating general fraud indicators as proof of a specific event.

## 6. Risk Assessment

Consider the available evidence collectively.

The assessment may consider:

- Machine learning risk score.
- Transaction characteristics.
- Related transaction patterns.
- Existing alert severity.
- Relevant investigation guidance.

A machine learning prediction is an estimate, not a confirmed fraud determination.

## 7. Investigation Findings

Findings should clearly distinguish:

**Observed evidence:** Facts directly retrieved from transaction or alert records.

**Analytical observations:** Interpretations derived from the available evidence.

**Knowledge-base guidance:** General investigation recommendations retrieved from supporting documents.

**Uncertainties:** Information that is missing or cannot be independently verified.

## 8. Recommended Actions

Depending on the evidence, possible recommendations include:

- No additional action based on currently available evidence.
- Request further transaction information.
- Review related account activity.
- Escalate for manual investigation.
- Continue monitoring for additional suspicious patterns.

Recommendations must be proportionate to the available evidence.

## 9. Reporting Requirements

Every investigation report should contain:

- Transaction identifier.
- Investigation date.
- Machine learning risk score and risk classification.
- Relevant transaction details.
- Evidence collected.
- Supporting knowledge-base references.
- Analytical findings.
- Identified limitations.
- Recommended next steps.

## 10. Disclaimer

This document provides illustrative investigation procedures for a fraud detection prototype. It does not represent an official financial institution policy or regulatory requirement.
