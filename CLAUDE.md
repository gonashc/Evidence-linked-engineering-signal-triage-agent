# Project rules for Claude Code

Evidence-linked engineering signal triage agent: a 3-day showcase from The Gen Academy *AI-Native Power User Workbook*, lab A11. Read `README.md`, `docs/rubric.md` and `docs/pilot_triage.md` before working.

## 1. Answer key: never touch it (most important)

- Never open, read, grep, list the contents of, or summarize anything under `data/answer_key/`.
- Never paste its contents into a prompt, a doc or a commit message.
- Only scripts in `scripts/eval/` may read it, and only at Day 3 scoring time.
- If a task seems to need it, stop and ask the user.
- `.claude/settings.json` denies these reads. Never weaken or work around those rules.

## 2. Approval gate

- Never commit or push without the user's explicit "approved".
- Before asking, show a summary of changed files and the full diff.
- Commit to `main` with clear messages. Never force-push. Never rewrite history.

## 3. Source of truth

- The rubric is `docs/rubric.md`. Don't copy it into other files; refer to it.
- Any rubric change needs the user's approval and a new dated row in its decision log.
- Never change a severity by hand without logging the reason.

## 4. Evidence rules

- Every claim links to the GitHub issue or comment it came from.
- Unknown fields stay blank. Never guess.
- Call something "verified fixed" only when a source confirms a successful retest.
- Feature requests, docs and support questions never count toward severity totals.

## 5. Data handling

- Public data only.
- Don't put reporters' usernames in published outputs.
- Don't amplify unfixed security issues beyond what is already public.
- The dashboard states it is an independent analysis, not affiliated with Angular or Google.

## 6. Stack and commands

- Python 3. Run scripts with `python3 -I`.
- `gh` CLI for GitHub data.
- Rebuild: `python3 -I scripts/normalize.py data/raw out`
- Planned: a JSON Schema validator, a static HTML dashboard on GitHub Pages, a weekly GitHub Actions refresh.
- Triage skill: `.claude/skills/signal-triage/SKILL.md`. Use it for any triage run.

## 7. Data layout (don't change)

- Window: issues created Oct 12 – Nov 11, 2026 in `angular/angular`, `angular/angular-cli`, `angular/components`. 163 issues, PRs excluded.
- `data/raw/`: raw GitHub search results.
- `data/derived/`: what the agent may see: `evidence_blind.csv`, `bodies.jsonl`, `blind_set_ids.txt`.
- `data/answer_key/`: scoring key for Day 3. Off limits (rule 1).

## 8. Day plan and status

- Day 1: done.
- Day 2: fetch comment threads, run the full triage, add the schema and validator, build the dashboard, set up the weekly Action.
- Day 3: accuracy check against the user's blind labels and maintainer labels, then the LinkedIn write-up.
