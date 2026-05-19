"""
Generate SentinelForge cybersecurity eventss simulator for batch and streaming ingestion.

This script simulates the kind of events that would normally come from
identity providers, firewalls, DNS resolvers, endpoint tools, and cloud audit logs.

It writes:
1. JSON Lines events for streaming-style ingestion.
2. CSV events for batch-style ingestion.

"""

from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

#print(PROJECT_ROOT)

SAMPLE_EVENTS_DIR = PROJECT_ROOT / "sample-events"

JSONL_OUTPUT_PATH = SAMPLE_EVENTS_DIR / "security_events.jsonl"
CSV_OUTPUT_PATH = SAMPLE_EVENTS_DIR / "security_events.csv"


def choose_event_type() -> str:
    """
    Choose a cybersecurity event type.

    Returns:
        A string representing the event type.
    """

    return random.choice(
        [
            "auth.login",
            "auth.mfa_challenge",
            "firewall.connection",
            "dns.query",
            "endpoint.process",
            "cloudtrail.api_call",
        ]
    )


def choose_country() -> str:
    """
    Choose a country code for the event.

    Returns:
        A two-letter country code.
    """

    return random.choice(["US", "CA", "GB", "IN", "DE", "BR", "RU", "CN", "NG"])


def calculate_risk_score(
    event_type: str,
    failed_login_count_1h: int,
    bytes_out: int,
    country: str,
) -> float:
    """
    Calculate a simple synthetic risk score.

    This is not a real security model. It is a rules-based placeholder
    that creates realistic-looking labels for ingestion practice.

    Args:
        event_type: Security event type.
        failed_login_count_1h: Failed login count in the last hour.
        bytes_out: Number of outbound bytes.
        country: Country code.

    Returns:
        A risk score between 0 and 1.
    """

    risk_score = 0.05

    if event_type.startswith("auth") and failed_login_count_1h >= 8:
        risk_score += 0.35

    if event_type == "firewall.connection" and bytes_out >= 1_000_000:
        risk_score += 0.30

    if country in {"RU", "CN", "NG"}:
        risk_score += 0.20

    risk_score += random.uniform(0.0, 0.15)

    return round(min(risk_score, 0.99), 3)


def label_from_risk_score(risk_score: float) -> str:
    """
    Convert a risk score into a human-readable class label.

    Args:
        risk_score: Numeric risk score.

    Returns:
        One of benign, suspicious, or malicious.
    """

    if risk_score >= 0.75:
        return "malicious"

    if risk_score >= 0.45:
        return "suspicious"

    return "benign"


def generate_event(event_number: int) -> dict[str, Any]:
    """
    Generate a single synthetic cybersecurity event.

    Args:
        event_number: Sequential event number.

    Returns:
        A dictionary representing one event.
    """

    event_type = choose_event_type()
    country = choose_country()
    failed_login_count_1h = random.randint(0, 20)
    bytes_out = random.randint(0, 2_000_000)

    risk_score = calculate_risk_score(
        event_type=event_type,
        failed_login_count_1h=failed_login_count_1h,
        bytes_out=bytes_out,
        country=country,
    )

    label = label_from_risk_score(risk_score)

    event_timestamp = datetime.now(timezone.utc) - timedelta(
        seconds=random.randint(0, 86_400)
    )

    return {
        "event_id": f"evt-{event_number:06d}",
        "event_timestamp": event_timestamp.isoformat(),
        "event_type": event_type,
        "user_id": f"user-{random.randint(1, 500):04d}",
        "source_ip": f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
        "country": country,
        "device_id": f"device-{random.randint(1, 250):04d}",
        "failed_login_count_1h": failed_login_count_1h,
        "bytes_out": bytes_out,
        "risk_score": risk_score,
        "label": label,
        "producer": "sentinelforge-event-generator",
    }


def write_jsonl(events: list[dict[str, Any]], output_path: Path) -> None:
    """
    Write events as JSON Lines.

    JSON Lines is useful for stream-like data because each line is one complete event.

    Args:
        events: List of event dictionaries.
        output_path: Output file path.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as jsonl_file:
        for event in events:
            jsonl_file.write(json.dumps(event) + "\n")


def write_csv(events: list[dict[str, Any]], output_path: Path) -> None:
    """
    Write events as CSV.

    CSV is useful for simple batch ingestion practice.

    Args:
        events: List of event dictionaries.
        output_path: Output file path.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not events:
        raise ValueError("Cannot write empty event list to CSV.")

    field_names = list(events[0].keys())

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(events)


def main() -> None:
    """
    Generate local batch and stream-style event files.
    """

    events = [generate_event(event_number) for event_number in range(1, 501)]

    write_jsonl(events=events, output_path=JSONL_OUTPUT_PATH)
    write_csv(events=events, output_path=CSV_OUTPUT_PATH)

    print("SentinelForge security event samples generated.")
    print(f"JSON Lines output: {JSONL_OUTPUT_PATH}")
    print(f"CSV output: {CSV_OUTPUT_PATH}")
    print(f"Record count: {len(events)}")


if __name__ == "__main__":
    main()