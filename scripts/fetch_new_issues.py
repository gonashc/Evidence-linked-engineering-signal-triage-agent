"""List issues created after the triaged window, for the dashboard's "Awaiting triage" section.

Usage: python3 -I scripts/fetch_new_issues.py --since 2026-11-11 --out out/new_issues.json \
           --exclude data/derived/evidence_blind.csv

Keeps only issue_id, url, title and created_utc. Labels, state, reactions and
usernames returned by the search API are dropped before anything is written.
The gh binary is taken from $GH_BIN, else PATH.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

REPOS = ["angular/angular", "angular/angular-cli", "angular/components"]

ap = argparse.ArgumentParser()
ap.add_argument("--since", required=True, help="YYYY-MM-DD, first day after the triaged window")
ap.add_argument("--out", required=True)
ap.add_argument("--exclude", help="CSV with an issue_id column (e.g. data/derived/evidence_blind.csv) to leave out")
args = ap.parse_args()

known = set()
if args.exclude:
    import csv
    with open(args.exclude, encoding="utf-8", newline="") as f:
        known = {r["issue_id"] for r in csv.DictReader(f)}

gh = os.environ.get("GH_BIN") or shutil.which("gh")
if not gh:
    sys.exit("gh CLI not found; install it or set GH_BIN")

items = []
for repo in REPOS:
    q = f"repo:{repo} is:issue created:>={args.since}"
    res = subprocess.run(
        [gh, "api", "-X", "GET", "search/issues", "-f", f"q={q}", "-f", "per_page=100", "--paginate",
         "--jq", ".items[] | {number, html_url, title, created_at}"],
        capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        sys.exit(f"{repo}: {res.stderr.strip()[:300]}")
    for line in res.stdout.splitlines():
        if line.strip():
            it = json.loads(line)
            if f"{repo.split('/')[1]}#{it['number']}" in known:
                continue
            items.append({"issue_id": f"{repo.split('/')[1]}#{it['number']}", "url": it["html_url"],
                          "title": it["title"], "created_utc": it["created_at"]})

os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
with open(args.out, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=1)
print(f"{len(items)} issues created since {args.since}")
