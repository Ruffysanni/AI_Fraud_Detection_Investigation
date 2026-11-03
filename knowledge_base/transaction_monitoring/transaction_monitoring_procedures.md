# Transaction Monitoring Procedures

**Document type:** Illustrative transaction monitoring guidance  
**Document ID:** TM-001  
**Version:** 1.0  
**Status:** Prototype knowledge-base document

## 1. Purpose

This document describes how transaction activity can be monitored to identify patterns that may require further investigation.

Transaction monitoring involves examining individual transactions and broader activity patterns to identify unusual behaviour.

## 2. Transaction Data Elements

The following transaction attributes may be useful during monitoring:

- Transaction identifier.
- Transaction type.
- Transaction amount.
- Transaction timestamp or sequence.
- Origin account identifier.
- Destination account identifier.
- Origin account balance before and after the transaction.
- Destination account balance before and after the transaction.

The availability of these fields depends on the source dataset and transaction system.

## 3. Transaction Amount Monitoring

Monitor transaction amounts for unusual changes.

Examples:
- A transaction substantially larger than previous activity.
- Repeated transactions with unusually high values.
- Sudden increases in transaction amounts.

The assessment should consider historical activity and available account context.

## 4. Transaction Frequency Monitoring

Monitor how frequently transactions occur.

Examples:
- Several transactions within a short period.
- Sudden increases in transaction frequency.
- Repeated transfers involving the same destination.

Frequency patterns should be evaluated against available transaction history rather than treated as automatic evidence of fraud.

## 5. Account Balance Monitoring

Examine account balances before and after transactions.

Examples:
- Large reductions in origin account balances.
- Unexpected increases in destination account balances.
- Transactions that reduce an account balance to zero.

Where balance information is available, compare the recorded values with the transaction amount.

## 6. Related Transaction Monitoring

Examine whether a transaction forms part of a broader sequence of activity.

Examples:
- Funds received and subsequently transferred.
- Multiple transactions involving the same accounts.
- Repeated transfers across related accounts.

Related transaction analysis requires reliable account identifiers and transaction records.

## 7. Alert Generation and Prioritisation

Monitoring systems may generate alerts when transaction activity meets defined risk conditions.

Alerts can be prioritised using:
- Machine learning risk scores.
- Rule-based indicators.
- Transaction characteristics.
- Related transaction patterns.

An alert indicates that activity requires attention. It does not establish that fraud has occurred.

## 8. Monitoring Limitations

Transaction monitoring may be affected by:
- Missing transaction records.
- Incomplete account histories.
- Incorrect or inconsistent data.
- Limited visibility into external accounts.
- Model prediction errors.
- Changes in legitimate customer behaviour.

These limitations should be considered when interpreting monitoring results.

## 9. Monitoring Recommendations

Monitoring findings may support:
- Further examination of transaction activity.
- Retrieval of additional account history.
- Review of associated alerts.
- Manual investigation.
- Continued monitoring.

## 10. Disclaimer

This document provides illustrative transaction monitoring guidance for a fraud detection prototype. It is not an official banking policy, regulatory standard or legal determination.