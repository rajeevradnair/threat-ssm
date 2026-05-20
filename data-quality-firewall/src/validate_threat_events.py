from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent

DEFAULT_INPUT_PATH = REPO_ROOT / "ingestion-control-plane" / "sample-events" / "security_events.csv"
CONTRACT_PATH = PROJECT_ROOT / "config" / "schema_contract.yaml"
REPORT_PATH = PROJECT_ROOT / "output" / "data_quality_report.json"


def load_contract(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def validate_required_columns(
    dataframe: pd.DataFrame,
    contract: dict[str, Any],
) -> dict[str, Any]:
    required_columns = contract["required_columns"]
    actual_columns = list(dataframe.columns)

    missing_columns = [
        column for column in required_columns if column not in actual_columns
    ]

    unexpected_columns = [
        column for column in actual_columns if column not in required_columns
    ]

    return {
        "check_name": "required_columns",
        "passed": len(missing_columns) == 0,
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
    }


def validate_missing_required_values(
    dataframe: pd.DataFrame,
    contract: dict[str, Any],
) -> dict[str, Any]:
    required_columns = contract["required_columns"]

    missing_counts = {}

    for column in required_columns:
        if column in dataframe.columns:
            missing_counts[column] = int(dataframe[column].isna().sum())

    total_missing = sum(missing_counts.values())

    threshold = contract["quality_thresholds"]["max_missing_required_value_count"]

    return {
        "check_name": "missing_required_values",
        "passed": total_missing <= threshold,
        "total_missing_required_values": total_missing,
        "missing_counts_by_column": missing_counts,
        "threshold": threshold,
    }


def validate_duplicate_event_ids(dataframe: pd.DataFrame) -> dict[str, Any]:
    duplicate_count = int(dataframe["event_id"].duplicated().sum())

    duplicate_ids = (
        dataframe.loc[dataframe["event_id"].duplicated(), "event_id"]
        .dropna()
        .astype(str)
        .tolist()
    )

    return {
        "check_name": "duplicate_event_ids",
        "passed": duplicate_count == 0,
        "duplicate_event_id_count": duplicate_count,
        "duplicate_event_ids": duplicate_ids[:20],
    }


def validate_timestamps(dataframe: pd.DataFrame) -> dict[str, Any]:
    parsed_timestamps = pd.to_datetime(
        dataframe["event_timestamp"],
        utc=True,
        errors="coerce",
    )

    invalid_count = int(parsed_timestamps.isna().sum())

    invalid_examples = (
        dataframe.loc[parsed_timestamps.isna(), "event_timestamp"]
        .astype(str)
        .head(20)
        .tolist()
    )

    return {
        "check_name": "valid_timestamps",
        "passed": invalid_count == 0,
        "invalid_timestamp_count": invalid_count,
        "invalid_examples": invalid_examples,
    }


def validate_labels(
    dataframe: pd.DataFrame,
    contract: dict[str, Any],
) -> dict[str, Any]:
    allowed_labels = set(contract["allowed_labels"])

    invalid_rows = dataframe[~dataframe["label"].isin(allowed_labels)]

    return {
        "check_name": "allowed_labels",
        "passed": len(invalid_rows) == 0,
        "invalid_label_count": int(len(invalid_rows)),
        "allowed_labels": sorted(allowed_labels),
        "invalid_label_examples": invalid_rows["label"].astype(str).head(20).tolist(),
    }


def validate_event_types(
    dataframe: pd.DataFrame,
    contract: dict[str, Any],
) -> dict[str, Any]:
    allowed_event_types = set(contract["allowed_event_types"])

    invalid_rows = dataframe[~dataframe["event_type"].isin(allowed_event_types)]

    return {
        "check_name": "allowed_event_types",
        "passed": len(invalid_rows) == 0,
        "invalid_event_type_count": int(len(invalid_rows)),
        "allowed_event_types": sorted(allowed_event_types),
        "invalid_event_type_examples": invalid_rows["event_type"]
        .astype(str)
        .head(20)
        .tolist(),
    }


def validate_numeric_ranges(
    dataframe: pd.DataFrame,
    contract: dict[str, Any],
) -> dict[str, Any]:
    numeric_rules = contract["numeric_rules"]

    violations = {}

    for column, rule in numeric_rules.items():
        if column not in dataframe.columns:
            continue

        numeric_values = pd.to_numeric(dataframe[column], errors="coerce")

        invalid_rows = dataframe[
            numeric_values.isna()
            | (numeric_values < rule["min"])
            | (numeric_values > rule["max"])
        ]

        violations[column] = {
            "invalid_count": int(len(invalid_rows)),
            "min_allowed": rule["min"],
            "max_allowed": rule["max"],
            "invalid_examples": invalid_rows[column].astype(str).head(20).tolist(),
        }

    total_invalid = sum(item["invalid_count"] for item in violations.values())

    return {
        "check_name": "numeric_ranges",
        "passed": total_invalid == 0,
        "total_invalid_numeric_values": total_invalid,
        "violations": violations,
    }


def build_data_quality_report(
    dataframe: pd.DataFrame,
    contract: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        validate_required_columns(dataframe, contract),
        validate_missing_required_values(dataframe, contract),
        validate_duplicate_event_ids(dataframe),
        validate_timestamps(dataframe),
        validate_labels(dataframe, contract),
        validate_event_types(dataframe, contract),
        validate_numeric_ranges(dataframe, contract),
    ]

    passed = all(check["passed"] for check in checks)

    return {
        "dataset_name": contract["dataset_name"],
        "contract_version": contract["contract_version"],
        "record_count": int(len(dataframe)),
        "passed": passed,
        "checks": checks,
    }


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)


def main() -> None:
    contract = load_contract(CONTRACT_PATH)
    dataframe = load_dataset(DEFAULT_INPUT_PATH)

    report = build_data_quality_report(
        dataframe=dataframe,
        contract=contract,
    )

    write_report(report, REPORT_PATH)

    print(f"Data quality report written to: {REPORT_PATH}")

    if report["passed"]:
        print("DATA QUALITY GATE: PASS")
    else:
        print("DATA QUALITY GATE: FAIL")


if __name__ == "__main__":
    main()