from __future__ import annotations

def should_send_to_human_review( predicted_label: str, confidence: float, risk_score: float,) -> bool:
    if confidence < 0.70:
        return True

    if risk_score > 0.85:
        return True

    if predicted_label == "unknown":
        return True

    if predicted_label == "benign" and risk_score > 0.75:
        return True

    return False


def main() -> None:
    sample_predictions = [
        {"event_id": "evt-000001", "predicted_label": "credential_attack", "confidence": 0.94, "risk_score": 0.91},
        {"event_id": "evt-000002", "predicted_label": "suspicious", "confidence": 0.58, "risk_score": 0.62},
        {"event_id": "evt-000003", "predicted_label": "benign", "confidence": 0.81, "risk_score": 0.90},
        {"event_id": "evt-000004", "predicted_label": "benign", "confidence": 0.96, "risk_score": 0.04},
        {"event_id": "evt-000005", "predicted_label": "unknown", "confidence": 0.67, "risk_score": 0.50},
    ]

    for prediction in sample_predictions:
        review_required = should_send_to_human_review(
            predicted_label=prediction["predicted_label"],
            confidence=prediction["confidence"],
            risk_score=prediction["risk_score"],
        )

        print(
            prediction["event_id"],
            prediction["predicted_label"],
            "review_required=",
            review_required,
        )


if __name__ == "__main__":
    main()