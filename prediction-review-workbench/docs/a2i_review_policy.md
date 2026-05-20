# SentinelForge Low-Confidence Human Review Policy

## Purpose

This document defines when SentinelForge should send a model prediction to human review.

This is the Amazon A2I-style workflow for cybersecurity predictions.

## Core Idea

A model should not automatically decide every event.

Some events should be reviewed by a human analyst when the model is uncertain, the risk is high, or the prediction conflicts with business rules.

## Review Triggers

Send an event to human review when any of the following are true:

| Trigger | Rule |
|---|---|
| Low confidence | Model confidence below 0.70 |
| High risk score | Risk score above 0.85 |
| Unknown label | Model predicts unknown |
| Conflicting signals | Model predicts benign but risk score is high |
| Sensitive asset | Event involves privileged user, payment system, or critical system |
| New pattern | Event type or country not commonly seen in training data |
| Drift suspicion | Feature distribution differs from training baseline |

## Example Decisions

| Prediction | Confidence | Risk Score | Action |
|---|---:|---:|---|
| credential_attack | 0.94 | 0.91 | Accept prediction and alert |
| benign | 0.96 | 0.04 | Accept prediction |
| suspicious | 0.58 | 0.62 | Send to human review |
| benign | 0.81 | 0.90 | Send to human review |
| unknown | 0.67 | 0.50 | Send to human review |

## Human Review Output

The reviewer should provide:

- corrected label
- analyst confidence
- explanation
- escalation flag
- review timestamp

## Future Retraining Use

Reviewed events should be stored as high-quality labeled examples for future retraining.