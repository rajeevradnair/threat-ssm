# SentinelForge Glue Catalog Notes

## Purpose

AWS Glue Data Catalog stores metadata for SentinelForge datasets stored in S3.

S3 stores the actual files.
Glue Data Catalog stores database, table, schema, partition, and location metadata.
Athena uses this metadata to query S3 data.

## Example Database

sentinelforge_threat_lake

## Example Tables

| Table | S3 Location | Purpose |
|---|---|---|
| raw_auth_events | s3://sentinelforge-ml-data/raw/auth/ | Raw authentication logs |
| raw_firewall_events | s3://sentinelforge-ml-data/raw/firewall/ | Raw firewall logs |
| raw_dns_events | s3://sentinelforge-ml-data/raw/dns/ | Raw DNS query logs |
| curated_threat_events | s3://sentinelforge-ml-data/curated/threat-events/ | Cleaned and normalized threat events |
| threat_risk_features | s3://sentinelforge-ml-data/features/threat-risk/ | Model-ready features |

## Glue Crawler Mental Model

A Glue crawler scans S3 paths and infers metadata such as:

- column names
- column data types
- partitions
- file format
- table location

After the crawler runs, Athena can query the discovered tables.

## Example Athena Query

```sql
SELECT
  label,
  COUNT(*) AS event_count
FROM curated_threat_events
GROUP BY label;