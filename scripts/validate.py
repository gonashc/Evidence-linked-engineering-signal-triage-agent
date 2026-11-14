"""Validate triage output against the schema and the skill's self-check.

Usage: python3 -I scripts/validate.py GROUPS.jsonl [--ids IDS.txt] [--evidence evidence_blind.csv]

--ids limits the coverage check to the issue IDs in that file (one per line),
e.g. data/derived/blind_set_ids.txt for the blind-set run.

Reads only the triage output and data/derived/. Never reads data/answer_key/.
Exits 1 if any check fails.
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schemas" / "triage_group.schema.json"
REPO_OF = {"angular": "angular", "angular-cli": "angular-cli", "components": "components"}

ap = argparse.ArgumentParser()
ap.add_argument("groups")
ap.add_argument("--ids")
ap.add_argument("--evidence", default=str(ROOT / "data" / "derived" / "evidence_blind.csv"))
args = ap.parse_args()
groups_path = Path(args.groups)
evidence_path = Path(args.evidence)

validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
errors = []

groups = []
for n, line in enumerate(groups_path.read_text(encoding="utf-8").splitlines(), 1):
    if not line.strip():
        continue
    try:
        g = json.loads(line)
    except json.JSONDecodeError as e:
        errors.append(f"line {n}: invalid JSON ({e})")
        continue
    for e in validator.iter_errors(g):
        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        errors.append(f"{g.get('group_id', f'line {n}')}: {path}: {e.message}")
    groups.append(g)

ids = Counter(g.get("group_id") for g in groups)
errors += [f"{gid}: duplicate group_id" for gid, c in ids.items() if c > 1]

with open(evidence_path, encoding="utf-8", newline="") as f:
    known = {row["issue_id"]: row["url"] for row in csv.DictReader(f)}
expected = set(known)
if args.ids:
    expected = {l.strip() for l in Path(args.ids).read_text(encoding="utf-8").splitlines() if l.strip()}
    errors += [f"--ids: {i} is not in the evidence table" for i in sorted(expected - set(known))]

seen = Counter()
# an @handle not followed by "/" (so npm scopes like @angular/core don't count)
handle = re.compile(r"(?<![\w/])@[A-Za-z0-9][A-Za-z0-9-]{0,38}(?![\w/-])")
for g in groups:
    gid = g.get("group_id")
    report_ids = set()
    for r in g.get("reports", []):
        iid, url = r.get("issue_id", ""), r.get("url", "")
        report_ids.add(iid)
        seen[iid] += 1
        if iid in known:
            base = known[iid]
            if not (url == base or url.startswith(base + "#issuecomment-")):
                errors.append(f"{gid}: {iid} url does not match its issue ({url})")
        else:
            m = re.match(r"^(angular|angular-cli|components)#(\d+)$", iid)
            want = f"https://github.com/angular/{REPO_OF.get(m.group(1), '')}/issues/{m.group(2)}" if m else ""
            if not url.startswith(want):
                errors.append(f"{gid}: {iid} url does not match its issue ({url})")
    for link in g.get("linked_groups", []):
        if link == gid:
            errors.append(f"{gid}: links to itself")
        elif link not in ids:
            errors.append(f"{gid}: linked group {link} does not exist")
    per_report = Counter()
    for q in g.get("evidence_quotes", []):
        per_report[q.get("issue_id")] += 1
        if q.get("issue_id") not in report_ids:
            errors.append(f"{gid}: quote cites {q.get('issue_id')}, which is not a report in this group")
        if len(q.get("quote", "").split()) > 15:
            errors.append(f"{gid}: quote from {q.get('issue_id')} is over 15 words")
    errors += [f"{gid}: {iid} has {c} quotes (max 1)" for iid, c in per_report.items() if c > 1]
    for field in ("title", "what_breaks", "rationale", "next_check", "status_from_comments"):
        # code in backticks (e.g. `@if`, `@fadeIn`) is template syntax, not a username
        if handle.search(re.sub(r"`[^`]*`", "", g.get(field, ""))):
            errors.append(f"{gid}: {field} contains an @handle; no usernames in outputs")

missing = sorted(expected - set(seen))
extra = sorted(set(seen) - expected)
if args.ids and extra:
    errors.append(f"{len(extra)} issues outside --ids: {', '.join(extra[:10])}")
if missing:
    errors.append(f"{len(missing)} issues not in any group: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}")

sev = Counter(g.get("severity") for g in groups)
scored = [g for g in groups if g.get("severity")]
unscored_bugs = [g["group_id"] for g in groups if g.get("category") in ("bug", "upstream") and not g.get("severity")]
errors += [f"{gid}: bug or upstream group has no severity" for gid in unscored_bugs]
splits = sorted(i for i, c in seen.items() if c > 1)

print(f"{len(groups)} groups covering {len(seen)} of {len(expected)} issues")
print("severity: " + ", ".join(f"{s}={sev.get(s, 0)}" for s in ("S1", "S2", "S3", "S4")) +
      f"; total {len(scored)} severity-rated groups; {sev.get(None, 0)} unrated")
print("categories: " + ", ".join(f"{k}={v}" for k, v in sorted(Counter(g.get('category') for g in groups).items())))
if splits:
    print(f"issues split across groups: {', '.join(splits)}")
if errors:
    print(f"\nFAIL: {len(errors)} problem(s)")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK")
