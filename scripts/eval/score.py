"""Day 3 accuracy check: agent vs. human blind labels vs. maintainer labels.

Usage:
  python3 -I scripts/eval/score.py data/triage/blind_groups.jsonl \
      [--human data/answer_key/blind_labels_naresh.csv] \
      [--key data/answer_key/answer_key_HIDDEN.csv] [--out out/eval]

This is the only script allowed to read data/answer_key/ (CLAUDE.md rule 1).
It scores the blind set only (data/derived/blind_set_ids.txt).

Stdout carries aggregate numbers only, never a per-issue label, so the agent
running it does not see individual answers. The per-issue comparison goes to
<out>/details.csv (out/ is gitignored) for the human to read.

Mapping choices (documented so the write-up can state them):
- Agent per issue: the severity and category of the group(s) holding it. An issue
  split across groups takes the most severe group.
- Maintainer severity from Angular priority labels: P0->S1, P1->S2, P2->S3,
  P3->S3, P4->S4, P5->S4. No priority label -> blank, not scored.
- Maintainer category from labels: feature -> feature request, docs -> docs,
  question/support -> support question, needs reproduction/clarification ->
  needs info, bug/regression -> bug; nothing matching -> blank, not scored.
- Blank values are never guessed and never counted as disagreements.
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEV = ["S1", "S2", "S3", "S4"]
CATS = {"bug", "upstream", "needs info", "feature request", "docs", "support question"}
PRIORITY_TO_SEV = {"P0": "S1", "P1": "S2", "P2": "S3", "P3": "S3", "P4": "S4", "P5": "S4"}

ap = argparse.ArgumentParser()
ap.add_argument("groups")
ap.add_argument("--human", default=str(ROOT / "data/answer_key/blind_labels_naresh.csv"))
ap.add_argument("--key", default=str(ROOT / "data/answer_key/answer_key_HIDDEN.csv"))
ap.add_argument("--ids", default=str(ROOT / "data/derived/blind_set_ids.txt"))
ap.add_argument("--out", default=str(ROOT / "out/eval"))
args = ap.parse_args()

for p in (args.human, args.key):
    if not os.path.isfile(p):
        sys.exit(f"not found: {p} (pass the right path with --human / --key)")

ids = [l.strip() for l in open(args.ids, encoding="utf-8") if l.strip()]


def norm_sev(s):
    s = (s or "").strip().upper()
    return s if s in SEV else ""


def norm_cat(s):
    s = re.sub(r"\s+", " ", (s or "").strip().lower())
    return s if s in CATS else ""


# agent
agent = {}
for line in open(args.groups, encoding="utf-8"):
    if not line.strip():
        continue
    g = json.loads(line)
    for r in g["reports"]:
        prev = agent.get(r["issue_id"])
        sev = g["severity"] or ""
        if prev is None or (sev and (not prev["sev"] or SEV.index(sev) < SEV.index(prev["sev"]))):
            agent[r["issue_id"]] = {"sev": sev, "cat": g["category"]}

# human
human, bad_human = {}, Counter()
with open(args.human, encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        iid = (row.get("issue_id") or "").strip()
        raw_s, raw_c = row.get("my_severity", ""), row.get("my_category", "")
        s, c = norm_sev(raw_s), norm_cat(raw_c)
        if raw_s.strip() and not s:
            bad_human["unrecognised severity values"] += 1
        if raw_c.strip() and not c:
            bad_human["unrecognised category values"] += 1
        human[iid] = {"sev": s, "cat": c}


def maint_cat(labels):
    l = labels.lower()
    if "feature" in l:
        return "feature request"
    if re.search(r"\bdocs?\b", l):
        return "docs"
    if "question" in l or "support" in l:
        return "support question"
    if "needs reproduction" in l or "needs: clarification" in l or "needs clarification" in l:
        return "needs info"
    if "bug" in l or "regression" in l:
        return "bug"
    return ""


maint = {}
with open(args.key, encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        pr = [p for p in (row.get("priority_label") or "").split(";") if p]
        sev = min((PRIORITY_TO_SEV[p] for p in pr if p in PRIORITY_TO_SEV), key=SEV.index, default="")
        labels = ";".join([row.get("area_labels") or "", row.get("other_labels") or ""])
        maint[row["issue_id"]] = {"sev": sev, "cat": maint_cat(labels), "state": row.get("state", ""),
                                  "reason": row.get("state_reason", "")}

missing = {name: sum(1 for i in ids if i not in src) for name, src in (("agent", agent), ("human", human), ("maintainer", maint))}


def compare(a, b, field):
    pairs = [(a.get(i, {}).get(field, ""), b.get(i, {}).get(field, "")) for i in ids]
    both = [(x, y) for x, y in pairs if x and y]
    exact = sum(x == y for x, y in both)
    res = {"n": len(both), "exact": exact}
    if field == "sev":
        res["within1"] = sum(abs(SEV.index(x) - SEV.index(y)) <= 1 for x, y in both)
        res["a_higher"] = sum(SEV.index(x) < SEV.index(y) for x, y in both)
        res["b_higher"] = sum(SEV.index(x) > SEV.index(y) for x, y in both)
    return res


def bugness(src, i):
    c = src.get(i, {}).get("cat", "")
    return "" if not c else ("rated" if c in ("bug", "upstream", "needs info") else "not rated")


def pct(k, n):
    return f"{k}/{n} ({100 * k / n:.0f}%)" if n else "n/a (0 comparable)"


print(f"Blind set: {len(ids)} issues. Missing records: " + ", ".join(f"{k}={v}" for k, v in missing.items()))
if bad_human:
    print("Human file: " + ", ".join(f"{v} {k}" for k, v in bad_human.items()) + " (treated as blank; fix spelling to score them)")
for na, a, nb, b in (("agent", agent, "human", human), ("agent", agent, "maintainer", maint), ("human", human, "maintainer", maint)):
    s, c = compare(a, b, "sev"), compare(a, b, "cat")
    bn = [(bugness(a, i), bugness(b, i)) for i in ids]
    bn = [(x, y) for x, y in bn if x and y]
    print(f"\n{na} vs {nb}")
    print(f"  severity exact:     {pct(s['exact'], s['n'])}")
    if s["n"]:
        print(f"  severity within 1:  {pct(s['within1'], s['n'])}; {na} higher {s['a_higher']}, {nb} higher {s['b_higher']}")
    print(f"  category exact:     {pct(c['exact'], c['n'])}")
    print(f"  rated vs not rated: {pct(sum(x == y for x, y in bn), len(bn))}")

for name, src in (("agent", agent), ("human", human), ("maintainer", maint)):
    d = Counter(src.get(i, {}).get("sev", "") or "-" for i in ids)
    print(f"\n{name} severity distribution: " + ", ".join(f"{k}={d.get(k, 0)}" for k in SEV + ["-"]))

os.makedirs(args.out, exist_ok=True)
out = Path(args.out) / "details.csv"
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["issue_id", "agent_sev", "human_sev", "maint_sev", "agent_cat", "human_cat", "maint_cat", "maint_state", "maint_reason"])
    for i in ids:
        A, H, M = agent.get(i, {}), human.get(i, {}), maint.get(i, {})
        w.writerow([i, A.get("sev", ""), H.get("sev", ""), M.get("sev", ""), A.get("cat", ""), H.get("cat", ""),
                    M.get("cat", ""), M.get("state", ""), M.get("reason", "")])
print(f"\nPer-issue comparison written to {out} (for the human; not printed here).")
