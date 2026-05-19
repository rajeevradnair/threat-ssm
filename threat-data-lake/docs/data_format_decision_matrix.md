# SentinelForge Data Format Decision Matrix

## Purpose

This document explains which data format SentinelForge should use at each stage of the cybersecurity ML lifecycle.

## Decision Matrix

| Format | Best Use | Strengths | Weaknesses | SentinelForge Usage |
|---|---|---|---|---|
| CSV | Simple tabular data and quick model input | Easy to read, easy to create, broadly supported | Weak schema, inefficient for large scans, poor nested data support | Small sample files and simple SageMaker training exports |
| JSON | Raw security logs and API events | Flexible, nested, common in logging systems | Larger file size, slower analytical scans | Raw auth, DNS, firewall, endpoint, and API logs |
| Parquet | Curated analytics and feature tables | Columnar, compressed, efficient with Athena and Spark-like tools | Not human-readable, less convenient for manual editing | Curated zone and feature zone |
| ORC | Large-scale big data analytics | Columnar, compressed, optimized for Hive-style workloads | Less commonly used in ML examples than Parquet | Alternative curated analytics format |
| Avro | Streaming and schema evolution | Strong schema support, good for event pipelines | Not as convenient for ad hoc analytics | Future streaming ingestion and event schema evolution |
| RecordIO | Efficient training input for some SageMaker algorithms | Efficient record-based training format | Less human-readable, algorithm-specific | Future SageMaker built-in algorithm experiments |

## Certification Memory Rules

1. CSV is simple and common for tabular training, but inefficient for large-scale analytics.
2. JSON is flexible and common for raw logs and APIs.
3. Parquet and ORC are columnar and efficient for analytics.
4. Avro is useful when schema evolution matters.
5. RecordIO is associated with efficient ML training records for some SageMaker algorithms.
6. SageMaker algorithm input requirements matter. Do not assume every algorithm accepts every format.
7. For many SageMaker built-in algorithms using CSV, the label is expected in the first column and headers are not used.

## SentinelForge Default Choices

| Data Lake Zone | Default Format | Reason |
|---|---|---|
| Raw | JSON or CSV | Preserve original source shape |
| Curated | Parquet | Efficient analytics and query performance |
| Features | Parquet | Efficient feature reuse and ML pipeline access |
| Training Export | CSV or RecordIO | Depends on SageMaker algorithm |
| Monitoring | JSON Lines or Parquet | JSON Lines for event logging, Parquet for analysis |