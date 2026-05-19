# SentinelForge Threat Data Lake Layout

## Purpose

SentinelForge stores cybersecurity machine learning data in a lake-style layout designed for ingestion, validation, feature engineering, model training, monitoring, and auditability.

The layout separates raw data, curated data, features, model artifacts, and monitoring outputs.

## Proposed S3 Bucket

s3://sentinelforge-ml-data/

## Zones

### Raw Zone

Raw data is stored exactly as received from source systems.

Example paths:

s3://sentinelforge-ml-data/raw/auth/year=2026/month=05/day=19/
s3://sentinelforge-ml-data/raw/firewall/year=2026/month=05/day=19/
s3://sentinelforge-ml-data/raw/dns/year=2026/month=05/day=19/

Rules:

- Do not overwrite raw data.
- Preserve original event shape.
- Store arrival timestamp.
- Encrypt all raw records.
- Restrict access because raw logs may contain sensitive identifiers.

### Curated Zone

Curated data is cleaned, normalized, deduplicated, and schema-validated.

Example path:

s3://sentinelforge-ml-data/curated/threat-events/year=2026/month=05/day=19/

Rules:

- Use consistent column names.
- Normalize event types and labels.
- Remove duplicates.
- Reject invalid timestamps.
- Store in Parquet for analytics and downstream ML processing.

### Feature Zone

Feature data contains model-ready signals derived from raw and curated events.

Example path:

s3://sentinelforge-ml-data/features/threat-risk/year=2026/month=05/day=19/

Example features:

- failed_login_rate_1h
- unusual_login_hour
- bytes_out_zscore
- country_risk_score
- ip_reputation_score
- rolling_session_risk

Rules:

- Prevent data leakage.
- Preserve feature generation timestamp.
- Keep offline features queryable.
- Align future online and offline feature definitions.

### Artifact Zone

Artifacts include model outputs, evaluation reports, metrics, and experiment outputs.

Example paths:

s3://sentinelforge-ml-data/artifacts/models/
s3://sentinelforge-ml-data/artifacts/evaluation/
s3://sentinelforge-ml-data/artifacts/experiments/

Rules:

- Version model artifacts.
- Preserve training configuration.
- Link model artifact to dataset version.
- Store evaluation metrics with model outputs.

### Monitoring Zone

Monitoring data includes inference logs, drift reports, baseline statistics, and endpoint metrics.

Example paths:

s3://sentinelforge-ml-data/monitoring/inference-logs/
s3://sentinelforge-ml-data/monitoring/model-monitor/
s3://sentinelforge-ml-data/monitoring/drift-reports/

Rules:

- Store prediction request metadata.
- Store prediction score and model version.
- Track drift signals.
- Support rollback and retraining decisions.

## Partitioning Strategy

Use date partitions for large datasets:

year=YYYY/month=MM/day=DD/

For high-volume sources, also partition by event_type:

event_type=auth/
event_type=firewall/
event_type=dns/

## File Format Strategy

- Raw zone: JSON or CSV depending on source system.
- Curated zone: Parquet.
- Feature zone: Parquet.
- Training export: CSV, Parquet, or RecordIO depending on algorithm.
- Monitoring zone: JSON Lines or Parquet.

## Security Controls

- Enable S3 bucket encryption with KMS.
- Block public access.
- Use least-privilege IAM roles.
- Enable versioning for important datasets.
- Use lifecycle policies for archival.
- Use Macie later to detect sensitive data.