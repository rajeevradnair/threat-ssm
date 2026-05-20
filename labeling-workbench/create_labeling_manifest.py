import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

INPUT_EVENTS_PATH = PROJECT_ROOT / "data" / "candidate_events.jsonl"
OUTPUT_MANIFEST_PATH = PROJECT_ROOT / "data" / "labeling_manifest.jsonl"

def read_jsonl(path: Path) -> list[dict]:
    event_records = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            event_records.append(json.loads(line))
    print(event_records)
    return event_records

def create_labeling_text(event: dict) -> str:
    return (
        f"Event ID: {event['event_id']} | "
        f"Event Type: {event['event_type']} | "
        f"Country: {event['country']} | "
        f"Failed logins in 1 hour: {event['failed_login_count_1h']} | "
        f"Bytes out: {event['bytes_out']} | "
        f"Risk score: {event['risk_score']} | "
        f"Context: {event['analyst_context']}"
    )

def create_manifest_record(event:dict) -> str:
    return {
        "source": create_labeling_text(event),
        "sentinelforge_event_id": event["event_id"]
    }

def write_jsonl(records: list[dict], path:Path) -> None:
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")


def main() -> None:
    events = read_jsonl(INPUT_EVENTS_PATH)

    manifest_records = []

    for event in events:
        manifest_record = create_manifest_record(event)
        manifest_records.append(manifest_record)

    write_jsonl(manifest_records, OUTPUT_MANIFEST_PATH)

    print(f"Created labeling manifest: {OUTPUT_MANIFEST_PATH}")
    print(f"Record count: {len(manifest_records)}")


if __name__ == "__main__":
    main()