# Evidence-linked engineering signal triage agent

An AI agent that reads a month of public issue reports, groups duplicates, ranks severity with a one-line rationale, and keeps a clickable evidence link on every call. Its severity calls are then scored against human and maintainer labels.

Built as a 3-day project from The Gen Academy *AI-Native Power User Workbook* (lab A11, "Slack to a weekly bug report"), using public GitHub issues instead of a private Slack channel.

## Status

| Day | Goal | State |
| --- | --- | --- |
| 1 | Scope, data pull, blind evidence table, rubric, 20-issue pilot | Done: rubric v0.2 approved Nov 12; pilot in `docs/pilot_triage.md` |
| Setup | Claude Code project rules, answer-key deny rules, triage skill, blind-labels template | Done Nov 12 |
| 2 | Full triage run, comment threads, dashboard, reusable skill, weekly refresh | Done Nov 14: 163 issues in 161 groups (5 S1, 17 S2, 84 S3, 13 S4; 42 not rated); validator, dashboard and weekly Action added |
| 3 | Accuracy check vs. human and maintainer labels, write-up | Done Nov 14: blind-set severity agreement with maintainers 74% exact for the agent, 60% for the human, both 100% within one level; draft post in `docs/linkedin_post.md` |

## Dataset (Day 1)

- **Repos:** `angular/angular`, `angular/angular-cli`, `angular/components`
- **Window:** issues created Oct 12 – Nov 11, 2026 (ET); retrieval time in `data/raw/retrieved_at.txt`
- **Records:** 163 issues (pull requests excluded)

## Layout

```
data/raw/          GitHub search API results, unmodified
data/raw/comments/ Comment threads per issue (gh API), unmodified
data/derived/      What the agent sees: evidence_blind.csv (one row per issue), bodies.jsonl,
                   comments.jsonl (no usernames), blind_set_ids.txt
data/triage/       Agent output: groups.jsonl (all 163 issues), blind_groups.jsonl (frozen blind-set calls)
data/answer_key/   Maintainer labels, state and close reason, hidden from the agent until scoring
docs/rubric.md     Severity rubric, grouping rules, decision log
docs/pilot_triage.md  Day 1 pilot: 20 reports, 19 groups
schemas/           JSON Schema for one issue group
scripts/           normalize.py, fetch_comments.py, validate.py, build_dashboard.py, fetch_new_issues.py
scripts/eval/      score.py: Day 3 scoring, the only code that reads data/answer_key/
.github/workflows/ weekly-refresh.yml: validate, list new issues, build and deploy the dashboard
```

## Reproduce

```sh
python3 -I scripts/normalize.py data/raw out
python3 -I scripts/fetch_comments.py --skip-ids data/derived/blind_set_ids.txt
python3 -m pip install -r requirements.txt   # jsonschema, for the validator
python3 -I scripts/validate.py data/triage/groups.jsonl
python3 -I scripts/fetch_new_issues.py --since 2026-11-11 --out out/new_issues.json --exclude data/derived/evidence_blind.csv
python3 -I scripts/build_dashboard.py data/triage/groups.jsonl site --new out/new_issues.json
```

The dashboard deploys to GitHub Pages from the weekly Action (Settings → Pages → Source: GitHub Actions).

## Working in this repo

- `CLAUDE.md` holds the project rules every Claude Code session follows: answer-key ban, approval gate, evidence and data-handling rules.
- `.claude/settings.json` denies reads of `data/answer_key/`.
- `.claude/skills/signal-triage/SKILL.md` is the triage procedure and output format. It applies `docs/rubric.md` and doesn't copy it.

## Method rules

- The agent sees only the title, issue body and comment thread. Labels, state and close reason stay in `data/answer_key/` until Day 3.
- The 25 blind-set issues were triaged from title and body only, the same inputs as the human blind labels, and frozen in `data/triage/blind_groups.jsonl` before scoring.
- Every claim links to the issue it came from. Unknown fields stay blank.
- Feature requests, docs and support questions are listed separately and never count toward severity totals.
- A fix is called verified only when a source confirms a successful retest.

## Known gaps

- Comment threads are read for the 138 non-blind issues only.
- The weekly Action lists new issues but does not triage them; that still needs an agent run.
- Older issues with new replies in the window are not included yet.

## Data and attribution

All data comes from public GitHub issues. Each record links back to its source. This is an independent analysis, not affiliated with or endorsed by the Angular team or Google. Issue text belongs to its authors; this repo stores it only to make the analysis reproducible.
