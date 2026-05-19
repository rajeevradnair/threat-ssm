"""
Lambda-style event transformer for SentinelForge ingestion.

This module simulates the transformation logic that could be used inside:

1. Amazon Data Firehose Lambda transformation
2. Kinesis Data Streams Lambda consumer
3. SQS Lambda worker
4. EventBridge Lambda target

The function normalizes fields, adds ingestion metadata, and classifies
where the event should land in the threat data lake.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any


def normalize_event_type(event_type: str) -> str:
    """
    Normalize detailed event types into broader security domains.

    Args:
        event_type: Raw event type.

    Returns:
        Normalized event domain.
    """

    if event_type.startswith("auth"):
        return "auth"

    if event_type.startswith("firewall"):
        return "firewall"

    if event_type.startswith("dns"):
        return "dns"

    if event_type.startswith("endpoint"):
        return "endpoint"

    if event_type.startswith("cloudtrail"):
        return "cloudtrail"

    return "unknown"


def choose_landing_zone(normalized_event_type: str) -> str:
    """
    Choose a raw data lake landing zone for the event.

    Args:
        normalized_event_type: Normalized event domain.

    Returns:
        A data lake path prefix.
    """

    return f"raw/{normalized_event_type}/"


def transform_security_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    Transform one security event.

    Args:
        event: Raw security event.

    Returns:
        Transformed security event with ingestion metadata.
    """

    normalized_event_type = normalize_event_type(str(event.get("event_type", "unknown")))

    transformed_event = {
        **event,
        "normalized_event_type": normalized_event_type,
        "landing_zone": choose_landing_zone(normalized_event_type),
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
        "ingestion_version": "sentinelforge-ingestion-v1",
    }

    return transformed_event


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Simulate an AWS Lambda handler for normal event payloads.

    Args:
        event: Incoming Lambda event.
        context: Lambda context object.

    Returns:
        Lambda response object.
    """

    transformed_event = transform_security_event(event)

    return {
        "statusCode": 200,
        "body": json.dumps(transformed_event),
    }


def firehose_transform_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Simulate an Amazon Data Firehose Lambda transformation handler.

    Firehose sends records encoded with base64. The transformer must decode
    each record, transform it, re-encode it, and return the result.

    Args:
        event: Firehose transformation event.
        context: Lambda context object.

    Returns:
        Firehose-compatible transformed records.
    """

    output_records = []

    for record in event.get("records", []):
        record_id = record["recordId"]
        encoded_payload = record["data"]

        decoded_payload = base64.b64decode(encoded_payload).decode("utf-8")
        raw_event = json.loads(decoded_payload)

        transformed_event = transform_security_event(raw_event)

        transformed_payload = json.dumps(transformed_event) + "\n"
        encoded_transformed_payload = base64.b64encode(
            transformed_payload.encode("utf-8")
        ).decode("utf-8")

        output_records.append(
            {
                "recordId": record_id,
                "result": "Ok",
                "data": encoded_transformed_payload,
            }
        )

    return {"records": output_records}


if __name__ == "__main__":
    sample_event = {
        "event_id": "evt-000001",
        "event_type": "auth.login",
        "user_id": "user-0001",
        "source_ip": "10.1.2.3",
        "country": "US",
        "failed_login_count_1h": 9,
        "bytes_out": 0,
        "risk_score": 0.67,
        "label": "suspicious",
    }

    response = lambda_handler(sample_event, context=None)
    #print(response)
    if response["statusCode"] == 200:
        print(json.dumps(json.loads(response["body"]), indent=2))
    else:
        print("Invalid response from lambda")