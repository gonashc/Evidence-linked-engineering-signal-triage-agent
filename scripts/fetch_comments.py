"""Fetch issue comment threads with the gh CLI and write a username-free derived file.

Usage: python3 -I scripts/fetch_comments.py [--skip-ids data/derived/blind_set_ids.txt]

Reads the issue list from data/derived/evidence_blind.csv and calls only
GET /repos/{owner}/{repo}/issues/{n}/comments, which returns comments, never
labels or state. Issues with comment_count 0 are skipped.

Writes:
  data/raw/comments/<repo>_<n>.json   raw API response (contains usernames; not published)
  data/derived/comments.jsonl         one line per comment: issue_id, url, created_utc,
                                      author_association, is_bot, body (no usernames)

The gh binary is taken from $GH_BIN, else PATH.
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOTS = {"angular-robot", "angular-automatic-lock-bot", "google-cla", "googlebot"}

ap = argparse.ArgumentParser()
ap.add_argument("--skip-ids", help="file of issue IDs to leave out (e.g. the blind set)")
ap.add_argument("--evidence", default=str(ROOT / "data/derived/evidence_blind.csv"))
ap.add_argument("--raw-dir", default=str(ROOT / "data/raw/comments"))
ap.add_argument("--out", default=str(ROOT / "data/derived/comments.jsonl"))
args = ap.parse_args()

gh = os.environ.get("GH_BIN") or shutil.which("gh")
if not gh:
    sys.exit("gh CLI not found; install it or set GH_BIN")

skip = set()
if args.skip_ids:
    skip = {l.strip() for l in open(args.skip_ids, encoding="utf-8") if l.strip()}

with open(args.evidence, encoding="utf-8", newline="") as f:
    issues = [r for r in csv.DictReader(f) if r["issue_id"] not in skip and int(r["comment_count"] or 0) > 0]

raw_dir = Path(args.raw_dir)
raw_dir.mkdir(parents=True, exist_ok=True)
lines, failed = [], []
for r in issues:
    owner_repo, n = r["repo"], r["number"]
    res = subprocess.run([gh, "api", "--paginate", "--slurp", f"repos/{owner_repo}/issues/{n}/comments?per_page=100"],
                         capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        failed.append(f"{r['issue_id']}: {res.stderr.strip()[:200]}")
        continue
    pages = json.loads(res.stdout)
    comments = [c for page in pages for c in page]
    (raw_dir / f"{owner_repo.split('/')[1]}_{n}.json").write_text(json.dumps(comments, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in comments:
        user = c.get("user") or {}
        login = (user.get("login") or "").lower()
        lines.append({
            "issue_id": r["issue_id"],
            "url": c["html_url"],
            "created_utc": c["created_at"],
            "author_association": c.get("author_association", ""),
            "is_bot": user.get("type") == "Bot" or login.endswith("[bot]") or login in BOTS,
            "body": c.get("body") or "",
        })

lines.sort(key=lambda x: (x["issue_id"], x["created_utc"]))
with open(args.out, "w", encoding="utf-8", newline="\n") as f:
    for x in lines:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
print(f"{len(issues)} issues queried, {len(lines)} comments written to {args.out}")
if failed:
    print(f"{len(failed)} failed:")
    for x in failed:
        print(" -", x)
    sys.exit(1)
