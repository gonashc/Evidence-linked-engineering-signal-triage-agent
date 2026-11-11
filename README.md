# Evidence-linked engineering signal triage agent

An AI agent that reads a month of public issue reports, groups duplicates, ranks severity with a one-line rationale, and keeps a clickable evidence link on every call. Its severity calls are then scored against human and maintainer labels.

Built as a 3-day project from The Gen Academy *AI-Native Power User Workbook* (lab A11, "Slack to a weekly bug report"), using public GitHub issues instead of a private Slack channel.

## Status

| Day | Goal | State |
| --- | --- | --- |
| 1 | Scope, data pull, blind evidence table, draft rubric, 20-issue pilot | Draft, awaiting rubric decisions |
| 2 | Full triage run, comment threads, dashboard, reusable skill, weekly refresh | Not started |
| 3 | Accuracy check vs. human and maintainer labels, write-up | Not started |

## Dataset (Day 1)

- **Repos:** `angular/angular`, `angular/angular-cli`, `angular/components`
- **Window:** issues created Oct 12 – Nov 11, 2026 (ET); retrieval time in `data/raw/retrieved_at.txt`
- **Records:** 163 issues (pull requests excluded)

## Layout

```
data/raw/          GitHub search API results, unmodified
data/derived/      What the agent sees: evidence_blind.csv (one row per issue), bodies.jsonl
data/answer_key/   Maintainer labels, state and close reason, hidden from the agent until scoring
docs/rubric.md     Severity rubric and grouping rules
scripts/           normalize.py: raw results -> blind evidence table + answer key
```

## Reproduce

```sh
python3 -I scripts/normalize.py data/raw out
```

## Method rules

- The agent sees only the title and issue body. Labels, state and close reason stay in `data/answer_key/` until Day 3.
- Every claim links to the issue it came from. Unknown fields stay blank.
- Feature requests, docs and support questions are listed separately and never count toward severity totals.
- A fix is called verified only when a source confirms a successful retest.

## Known gaps

- Comment threads are not yet read, so status and workarounds from replies are missing.
- Older issues with new replies in the window are not included yet.

## Data and attribution

All data comes from public GitHub issues. Each record links back to its source. This is an independent analysis, not affiliated with or endorsed by the Angular team or Google. Issue text belongs to its authors; this repo stores it only to make the analysis reproducible.
