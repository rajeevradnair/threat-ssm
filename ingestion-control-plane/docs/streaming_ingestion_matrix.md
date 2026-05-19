# SentinelForge Streaming Ingestion Decision Matrix

## Purpose

This document explains how SentinelForge chooses between batch ingestion,
streaming ingestion, queueing, fanout, event routing, and cataloging services.

## Core Mental Model

- S3 stores durable files.
- Kinesis Data Streams ingests real-time streams.
- Amazon Data Firehose delivers streaming data to destinations such as S3.
- Lambda performs lightweight event transformation.
- SQS decouples producers from consumers and supports retries.
- SNS fans out notifications to multiple subscribers.
- EventBridge routes events based on event patterns.
- Glue Data Catalog stores metadata so data can be queried and processed.

## Decision Matrix

| Need | Best Service | Why |
|---|---|---|
| Store daily batch files | S3 | Durable object storage for raw logs |
| Ingest continuous login events | Kinesis Data Streams | Real-time streaming, replay, ordered records within shard |
| Deliver streaming firewall logs to S3 | Amazon Data Firehose | Managed delivery, buffering, optional Lambda transform |
| Transform small event payloads | Lambda | Lightweight event-driven compute |
| Buffer enrichment jobs | SQS | Decoupling, retry, dead-letter queues |
| Notify multiple systems of a high-risk alert | SNS | Pub/sub fanout |
| Route business events to workflows | EventBridge | Event bus with pattern-based routing |
| Discover schema for S3 datasets | Glue Data Catalog and Crawler | Metadata catalog for Athena, Glue ETL, and analytics |
| Query S3 logs with SQL | Athena + Glue Catalog | Serverless SQL over cataloged S3 data |

## SentinelForge Example Flows

### Flow 1: Batch Firewall Export

firewall export
→ S3 raw/firewall/
→ Glue crawler
→ Glue Data Catalog table
→ Athena query
→ SageMaker Processing later

### Flow 2: Real-Time Login Stream

identity provider
→ Kinesis Data Streams
→ Lambda consumer
→ suspicious event enrichment
→ S3 raw/auth/

### Flow 3: Simple Stream Delivery

firewall sensor
→ Amazon Data Firehose
→ Lambda transform
→ S3 raw/firewall/

### Flow 4: Low-Confidence Event Review Queue

model prediction
→ low confidence event
→ SQS queue
→ Lambda worker
→ human review workflow later

### Flow 5: High-Risk Alert Fanout

high-risk event
→ SNS topic
→ SOC email
→ incident Lambda
→ SQS investigation queue

### Flow 6: Dataset Ready Event

curated dataset created
→ EventBridge event
→ rule match
→ start downstream ML workflow later

## Design Rules

1. Kinesis Data Streams = real-time streaming ingestion.
2. Amazon Data Firehose = managed stream delivery to storage/analytics destinations.
3. SQS = queue, decoupling, retries, dead-letter queue.
4. SNS = fanout notification to multiple subscribers.
5. EventBridge = event bus and rule-based routing.
6. Lambda = lightweight event-driven compute.
7. Glue Data Catalog = metadata catalog for S3 datasets.
8. Athena uses Glue Data Catalog metadata to query S3 data.
9. Batch files generally land directly in S3.
10. Streaming data often needs buffering before landing in S3.

## Common Wrong Mental Models

| Wrong Mental Model | Correct Mental Model |
|---|---|
| Kinesis and Firehose are the same | Kinesis is a stream; Firehose is managed delivery |
| SQS and SNS are the same | SQS queues work; SNS broadcasts notifications |
| EventBridge is just SNS | EventBridge routes events using event patterns |
| Lambda is a data lake | Lambda transforms or reacts; it does not store large datasets |
| Glue stores data | Glue Catalog stores metadata; S3 stores data |
| Athena stores data | Athena queries data; it does not store the dataset |