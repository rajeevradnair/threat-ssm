# SentinelForge Human Labeling Policy

## Purpose

This policy defines how human analysts should label cybersecurity events for SentinelForge.

## Labeling Goal

The goal is to create high-quality supervised learning labels for threat classification.

The label should answer:

"What is the best threat category for this event based on the evidence shown?"

## Allowed Labels

- benign
- suspicious
- credential_attack
- exfiltration
- malware_like
- unknown

## Worker Instructions

1. Read the full event summary.
2. Identify the strongest evidence.
3. Choose the most specific label supported by the evidence.
4. Use `unknown` if the event does not contain enough information.
5. Do not label based only on risk score.
6. Use risk score as a hint, not as the final answer.
7. Prefer `credential_attack` when login behavior clearly suggests credential abuse.
8. Prefer `exfiltration` when outbound data movement is the main concern.
9. Prefer `malware_like` when endpoint, process, or DNS behavior resembles malware.
10. Use `suspicious` when the event is concerning but not specific enough.

## Quality Rules

- If two labels seem possible, choose the more specific label only when evidence supports it.
- If evidence is incomplete, choose `unknown`.
- Do not invent missing context.
- Do not overuse `malicious` as a generic label.
- Escalate ambiguous events for second review.

## Examples

| Event Summary | Correct Label | Reason |
|---|---|---|
| Many failed logins from unusual country | credential_attack | Identity attack pattern |
| Large outbound transfer to unusual destination | exfiltration | Data movement risk |
| Suspicious process contacting rare domain | malware_like | Endpoint and DNS behavior |
| Normal login from usual country | benign | No clear threat signal |
| Moderate risk but unclear evidence | suspicious | Concerning but not specific |
| Missing core fields | unknown | Insufficient evidence |