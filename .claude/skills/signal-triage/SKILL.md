---
name: signal-triage
description: Use to triage a batch of GitHub issues into severity-ranked, evidence-linked issue groups using docs/rubric.md.
---

# Signal triage

The rubric is `docs/rubric.md`. Read it before every run and apply it exactly. This skill gives the procedure only. Don't restate or change the rubric here.

## Inputs

- A set of issue records: title, body and, when available, comments.
- Use only `data/derived/` (and fetched comment threads).
- Never use labels, state or close reason. Never read `data/answer_key/`.

## Procedure

a. **Extract evidence.** Write one evidence record per symptom: action, observed result, expected result, environment/version, regression claim, repro link, error text. Leave unknown fields blank.
b. **Categorize.** Assign one category from the rubric.
c. **Group.** Apply the rubric's merge / link / split rules. Never merge on title similarity alone; keep ambiguous pairs separate and flag them.
d. **Assign severity.** Bugs only. Apply the rubric's adjustments in the rubric's order.
e. **Explain.** Write a one-sentence rationale and one next engineering check.
f. **Link.** List linked groups.

## Output

One JSON object per issue group:

```json
{
  "group_id": "",
  "severity": "S1 | S2 | S3 | S4 | null",
  "category": "",
  "title": "",
  "what_breaks": "",
  "rationale": "",
  "next_check": "",
  "reports": [{"issue_id": "", "url": ""}],
  "linked_groups": [],
  "regression": "yes | no | unclear | (blank)",
  "status_from_comments": "",
  "needs_info": false,
  "evidence_quotes": []
}
```

- `status_from_comments`: blank if comments were not read.
- `evidence_quotes`: at most 1 per report, each 15 words or fewer, copied verbatim.
- No reporter usernames in any field.

## Self-check before returning

- [ ] Every report has a URL.
- [ ] Severity totals match the number of bug groups.
- [ ] No answer-key fields (labels, state, close reason) were used.
- [ ] Every non-bug has `severity: null`.

Fix any failure before returning the output.
