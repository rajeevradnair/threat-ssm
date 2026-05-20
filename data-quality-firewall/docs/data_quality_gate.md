# SentinelForge Data Quality Gate

## Purpose

This document defines the rules that determine whether a SentinelForge dataset is safe to use for machine learning training.

## Core Principle

No dataset should move into preprocessing, feature engineering, or training unless it passes the data quality gate.

## Why This Matters

Cybersecurity ML models are sensitive to bad data.

Bad data can cause:

- failed training jobs
- incorrect features
- false positives
- false negatives
- label noise
- data leakage
- unreliable evaluation metrics
- unsafe model deployment

## Required Checks

| Check | Purpose | Gate Rule |
|---|---|---|
| Required columns | Ensure expected schema is present | No missing required columns |
| Missing values | Ensure required fields are populated | No missing required values |
| Duplicate event IDs | Prevent duplicated examples | No duplicate event IDs |
| Timestamp validity | Support time-based features | No invalid timestamps |
| Label validity | Ensure target labels are known | Labels must be approved |
| Event type validity | Detect schema/source drift | Event types must be approved |
| Numeric ranges | Prevent impossible values | Values must be inside allowed range |

## Pass Criteria

The dataset passes only if all required checks pass.

## Fail Criteria

The dataset fails if any critical rule fails.

Examples:

- missing `event_id`
- duplicate `event_id`
- invalid timestamp
- unknown label
- unknown event type
- negative `bytes_out`
- risk score outside 0 to 1

## Failure Handling

If the dataset fails:

1. Stop training.
2. Write data quality report.
3. Quarantine failed records.
4. Notify data owner.
5. Fix upstream ingestion or schema contract.
6. Re-run validation.

## AWS Mapping

| Local SentinelForge Artifact | AWS Equivalent |
|---|---|
| schema_contract.yaml | Glue Data Quality ruleset |
| validate_threat_events.py | Glue Data Quality evaluation / Processing Job validation |
| data_quality_report.json | Glue Data Quality result / Processing output |
| data_quality_gate.md | Pipeline quality policy |
| quarantine/ | S3 quarantine prefix |

## Training Gate Rule

If `data_quality_report.json` contains:

```json
"passed": false