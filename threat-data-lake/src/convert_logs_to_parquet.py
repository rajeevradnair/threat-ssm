"""
Convert synthetic SentinelForge cybersecurity events from CSV to Parquet.

This script demonstrates the first data engineering step in the SentinelForge
machine learning lifecycle:

raw security events -> tabular dataset -> efficient Parquet file

The goal is not advanced modeling yet. The goal is to understand how raw
security logs become durable, queryable, model-ready data.
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_AUTH_DIR = PROJECT_ROOT / "raw" / "auth"
CURATED_DIR = PROJECT_ROOT / "curated" / "threat-events"

CSV_OUTPUT_PATH = RAW_AUTH_DIR / "threat_events_sample.csv"
PARQUET_OUTPUT_PATH = CURATED_DIR / "threat_events.parquet"


def generate_synthetic_threat_events(row_count: int = 100) -> list[dict[str, object]]:
    """
    Generate synthetic cybersecurity events.

    Each event is intentionally simple. Later days will add validation,
    labeling, feature engineering, and model training.

    Args:
        row_count: Number of synthetic events to generate.

    Returns:
        A list of dictionaries. Each dictionary represents one security event.
    """

    event_types = ["auth", "firewall", "dns"]
    countries = ["US", "CA", "GB", "IN", "DE", "BR", "RU", "CN", "NG"]
    labels = ["benign", "suspicious", "malicious"]

    events: list[dict[str, object]] = []

    now = datetime.now(timezone.utc)

    for event_number in range(1, row_count + 1):
        event_type = random.choice(event_types)
        country = random.choice(countries)

        failed_login_count_1h = random.randint(0, 20)
        bytes_out = random.randint(0, 2_000_000)

        is_high_risk_country = country in {"RU", "CN", "NG"}
        has_many_failed_logins = failed_login_count_1h >= 10
        has_large_data_transfer = bytes_out >= 1_000_000

        if has_many_failed_logins and is_high_risk_country:
            label = "malicious"
            risk_score = round(random.uniform(0.80, 0.99), 3)
        elif has_large_data_transfer or has_many_failed_logins:
            label = "suspicious"
            risk_score = round(random.uniform(0.45, 0.79), 3)
        else:
            label = "benign"
            risk_score = round(random.uniform(0.01, 0.44), 3)

        event_timestamp = now - timedelta(minutes=random.randint(0, 1440))

        event = {
            "event_id": f"evt-{event_number:05d}",
            "event_timestamp": event_timestamp.isoformat(),
            "event_type": event_type,
            "user_id": f"user-{random.randint(1, 50):03d}",
            "source_ip": f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}",
            "country": country,
            "failed_login_count_1h": failed_login_count_1h,
            "bytes_out": bytes_out,
            "risk_score": risk_score,
            "label": label,
        }

        events.append(event)

    return events


def write_events_to_csv(events: list[dict[str, object]], output_path: Path) -> None:
    """
    Write synthetic events to a CSV file.

    CSV is useful for small examples and simple tabular model input.
    It is not the best long-term analytics format for large data lakes.

    Args:
        events: Synthetic cybersecurity events.
        output_path: Local path where the CSV file should be written.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not events:
        raise ValueError("No events were provided. Cannot write an empty CSV file.")

    field_names = list(events[0].keys())

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(events)


def convert_csv_to_parquet(csv_path: Path, parquet_path: Path) -> None:
    """
    Convert a CSV file into Parquet.

    Parquet is useful for curated ML datasets because it is compressed,
    columnar, and efficient for analytics engines such as Athena.

    Args:
        csv_path: Path to the source CSV file.
        parquet_path: Path where the Parquet output should be written.
    """

    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    threat_events = pd.read_csv(csv_path)

    threat_events["event_timestamp"] = pd.to_datetime(
        threat_events["event_timestamp"],
        utc=True,
        errors="coerce",
    )

    threat_events.to_parquet(parquet_path, index=False)


def print_dataset_summary(csv_path: Path, parquet_path: Path) -> None:
    """
    Print a short summary so the learner can inspect what was created.

    Args:
        csv_path: Path to the generated CSV file.
        parquet_path: Path to the generated Parquet file.
    """

    threat_events = pd.read_parquet(parquet_path)

    print("SentinelForge threat event dataset created successfully.")
    print(f"CSV path: {csv_path}")
    print(f"Parquet path: {parquet_path}")
    print()
    print("Record count:", len(threat_events))
    print()
    print("Label distribution:")
    print(threat_events["label"].value_counts())
    print()
    print("Event type distribution:")
    print(threat_events["event_type"].value_counts())
    print()
    print("Preview:")
    print(threat_events.head(5))


def main() -> None:
    """
    Run the local Day 1 data lake build.
    """

    events = generate_synthetic_threat_events(row_count=100_000)

    write_events_to_csv(
        events=events,
        output_path=CSV_OUTPUT_PATH,
    )

    convert_csv_to_parquet(
        csv_path=CSV_OUTPUT_PATH,
        parquet_path=PARQUET_OUTPUT_PATH,
    )

    print_dataset_summary(
        csv_path=CSV_OUTPUT_PATH,
        parquet_path=PARQUET_OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()