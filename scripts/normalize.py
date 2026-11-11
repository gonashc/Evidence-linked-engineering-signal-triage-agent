"""Normalize raw GitHub search results into a blind evidence table and a hidden answer key.

Usage: python3 -I scripts/normalize.py data out
"""
import csv, json, re, sys, glob, os
from datetime import datetime, timezone, timedelta

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
ET = timezone(timedelta(hours=-5))  # window is entirely in EST after Nov 1; EDT before. Store UTC + note.

def sections(body):
    """Split a GitHub issue-form body into {heading: text}."""
    parts = {}
    if not body:
        return parts
    for m in re.finditer(r"^### (.+?)\n(.*?)(?=^### |\Z)", body, re.S | re.M):
        txt = m.group(2).strip()
        if txt in ("_No response_", "```true\n\n```", "```true\n```"):
            txt = ""
        parts[m.group(1).strip()] = txt
    return parts

def pick(sec, *keys):
    for k, v in sec.items():
        if any(key.lower() in k.lower() for key in keys):
            return v
    return ""

def clean(s, n):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s[:n]

def version(env):
    m = re.search(r"Angular(?: CLI)?\s*:\s*([0-9][\w.\-]*)", env or "")
    return m.group(1) if m else ""

rows, key = [], []
for f in sorted(glob.glob(f"{src}/angular_*.json")):
    repo = os.path.basename(f)[:-5].replace("_", "/", 1)
    items = []
    with open(f) as fh:
        txt = fh.read()
    # --paginate concatenates JSON objects
    for chunk in re.split(r"(?<=\})\s*(?=\{\"total_count\")", txt):
        items += json.loads(chunk)["items"]
    for it in items:
        if it.get("pull_request"):
            continue
        sec = sections(it.get("body") or "")
        bug_form = any("source of the bug" in k for k in sec) or any("minimal reproduction" in k.lower() for k in sec)
        feat_form = any("feature request" in k.lower() for k in sec) or any("proposed solution" in k.lower() for k in sec)
        desc = pick(sec, "Description") or (it.get("body") or "")
        repro = pick(sec, "minimal reproduction", "reproduction")
        err = pick(sec, "exception or error")
        env = pick(sec, "environment")
        regress_raw = pick(sec, "regression")
        if re.search(r"\[x\]", regress_raw, re.I) or re.match(r"\s*yes", regress_raw, re.I):
            regress = "yes"
        elif re.search(r"\[ \]", regress_raw) or re.match(r"\s*no", regress_raw, re.I):
            regress = "no"
        elif regress_raw:
            regress = "unclear"
        else:
            regress = ""
        iid = f"{repo.split('/')[1]}#{it['number']}"
        rows.append({
            "issue_id": iid,
            "repo": repo,
            "number": it["number"],
            "url": it["html_url"],
            "title": it["title"],
            "created_utc": it["created_at"],
            "author_association": it["author_association"],
            "form": "bug" if bug_form else ("feature" if feat_form else "freeform"),
            "package_claimed": clean(pick(sec, "package"), 120),
            "regression_claimed": clean(regress, 40),
            "angular_version": version(env),
            "has_repro_link": "yes" if re.search(r"https?://", repro) else "no",
            "has_error_text": "yes" if clean(err, 5) else "no",
            "description_excerpt": clean(desc, 600),
            "body_chars": len(it.get("body") or ""),
            "comment_count": it["comments"],
            "reactions": it.get("reactions", {}).get("total_count", 0),
        })
        labels = [l["name"] for l in it["labels"]]
        key.append({
            "issue_id": iid,
            "state": it["state"],
            "state_reason": it.get("state_reason") or "",
            "closed_utc": it.get("closed_at") or "",
            "priority_label": ";".join(l for l in labels if re.fullmatch(r"P[0-5]", l)),
            "area_labels": ";".join(l for l in labels if l.lower().startswith("area:")),
            "other_labels": ";".join(l for l in labels if not re.fullmatch(r"P[0-5]", l) and not l.lower().startswith("area:")),
        })
        # full body kept separately for the agent's reading, without labels/state
        with open(f"{out}/bodies.jsonl", "a") as bf:
            bf.write(json.dumps({"issue_id": iid, "url": it["html_url"], "title": it["title"], "body": it.get("body") or ""}) + "\n")

rows.sort(key=lambda r: r["created_utc"])
for name, data in (("evidence_blind.csv", rows), ("answer_key_HIDDEN.csv", key)):
    with open(f"{out}/{name}", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
        w.writeheader(); w.writerows(data)
print(len(rows), "issues;", sum(r["form"] == "bug" for r in rows), "bug-form;",
      sum(r["form"] == "feature" for r in rows), "feature-form;", sum(r["form"] == "freeform" for r in rows), "freeform")
