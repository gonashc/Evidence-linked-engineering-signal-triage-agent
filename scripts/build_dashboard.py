"""Build the static dashboard from triage output.

Usage: python3 -I scripts/build_dashboard.py data/triage/groups.jsonl site [--new out/new_issues.json]

Reads only the triage output (and, optionally, the list of issues created after the
triaged window). Never reads data/answer_key/ or data/raw/. Writes site/index.html.
No reporter usernames, labels or maintainer state appear on the page.
"""
import argparse
import html
import json
import os
from collections import Counter
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("groups")
ap.add_argument("out_dir")
ap.add_argument("--new", help="JSON list of {issue_id, url, title, created_utc} created after the window")
args = ap.parse_args()

groups = [json.loads(l) for l in open(args.groups, encoding="utf-8") if l.strip()]
new = json.load(open(args.new, encoding="utf-8")) if args.new and os.path.exists(args.new) else None

SEV = ["S1", "S2", "S3", "S4"]
RATED = {"bug", "upstream", "needs info"}
SEV_LABEL = {"S1": "Critical", "S2": "High", "S3": "Medium", "S4": "Low"}
e = html.escape


def repo_of(g):
    return g["reports"][0]["issue_id"].split("#")[0]


def short(iid):
    return iid.replace("angular-cli#", "cli#").replace("components#", "components#").replace("angular#", "angular#")


def sev_key(g):
    return (SEV.index(g["severity"]) if g["severity"] else 9, g["group_id"])


def code(s):
    # render `code` spans from the triage text, everything else escaped
    parts = s.split("`")
    return "".join(f"<code>{e(p)}</code>" if i % 2 else e(p) for i, p in enumerate(parts))


rated = sorted((g for g in groups if g["category"] in RATED and g["severity"]), key=sev_key)
other = sorted((g for g in groups if g not in rated), key=lambda g: (g["category"], g["group_id"]))
counts = Counter(g["severity"] for g in rated)
issues = {r["issue_id"] for g in groups for r in g["reports"]}
repos = Counter(i.split("#")[0] for i in issues)


def row(g):
    reports = " ".join(f'<a href="{e(r["url"])}">{e(short(r["issue_id"]))}</a>' for r in g["reports"])
    links = " ".join(f'<a href="#{e(l)}">{e(l)}</a>' for l in g["linked_groups"]) or ""
    flags = []
    if g["regression"] == "yes":
        flags.append('<span class="flag">regression</span>')
    if g["needs_info"]:
        flags.append('<span class="flag warn">needs info</span>')
    if g["category"] == "upstream":
        flags.append('<span class="flag">upstream</span>')
    quote = "".join(f'<blockquote>“{e(q["quote"])}”</blockquote>' for q in g["evidence_quotes"])
    status = f'<p class="status"><b>From comments:</b> {code(g["status_from_comments"])}</p>' if g["status_from_comments"] else ""
    sev = g["severity"] or "—"
    return f"""
<tr id="{e(g['group_id'])}" data-sev="{e(sev)}" data-repo="{e(repo_of(g))}" data-cat="{e(g['category'])}">
  <td><span class="sev sev-{e(sev)}">{e(sev)}</span></td>
  <td>
    <div class="title">{code(g['title'])}</div>
    <div class="meta">{reports} {''.join(flags)}</div>
    <details><summary>Details</summary>
      <p><b>What breaks:</b> {code(g['what_breaks'])}</p>
      <p><b>Why this level:</b> {code(g['rationale'])}</p>
      <p><b>Next check:</b> {code(g['next_check'])}</p>
      {status}{quote}
      {f'<p><b>Linked:</b> {links}</p>' if links else ''}
    </details>
  </td>
  <td class="gid">{e(g['group_id'])}</td>
</tr>"""


new_html = ""
if new is not None:
    items = sorted(new, key=lambda x: x["created_utc"], reverse=True)
    lis = "".join(
        f'<li><a href="{e(i["url"])}">{e(short(i["issue_id"]))}</a> {e(i["title"])} <span class="muted">{e(i["created_utc"][:10])}</span></li>'
        for i in items[:100])
    more = f'<p class="muted">Showing the 100 most recent of {len(items)}.</p>' if len(items) > 100 else ""
    new_html = f"""
<section>
  <h2>Awaiting triage <span class="muted">({len(items)})</span></h2>
  <p class="muted">Issues created after the triaged window, found by the weekly refresh. Not yet grouped or rated.</p>
  {more}<ul class="new">{lis or '<li class="muted">None</li>'}</ul>
</section>"""

built = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
cards = "".join(
    f'<div class="card"><span class="sev sev-{s}">{s}</span><b>{counts.get(s, 0)}</b><span class="muted">{SEV_LABEL[s]}</span></div>'
    for s in SEV)
cat_counts = Counter(g["category"] for g in other)
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Angular Signal Triage</title>
<meta name="description" content="Independent, evidence-linked severity triage of public Angular GitHub issues.">
<style>
:root {{
  --bg: #fbfbfa; --fg: #1d1d1b; --muted: #6b6b66; --line: #e3e2dd; --card: #ffffff;
  --s1: #b42318; --s2: #c4500d; --s3: #8a6d00; --s4: #4b5563; --link: #1f5fbf; --flag: #eef1f6;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #161615; --fg: #ecebe7; --muted: #a3a29c; --line: #33322f; --card: #1f1f1d;
    --s1: #ff8a80; --s2: #ffab6e; --s3: #e6c84f; --s4: #b8c0cc; --link: #8ab4ff; --flag: #2a2d33;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #161615; --fg: #ecebe7; --muted: #a3a29c; --line: #33322f; --card: #1f1f1d;
  --s1: #ff8a80; --s2: #ffab6e; --s3: #e6c84f; --s4: #b8c0cc; --link: #8ab4ff; --flag: #2a2d33;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 24px 16px 64px; }}
a {{ color: var(--link); }}
h1 {{ font-size: 1.6rem; margin: 0 0 4px; }}
h2 {{ font-size: 1.15rem; margin: 32px 0 8px; }}
.muted {{ color: var(--muted); }}
.notice {{ border: 1px solid var(--line); background: var(--card); padding: 10px 14px; border-radius: 8px; margin: 16px 0; font-size: .9rem; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 16px 0; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 12px; display: flex; gap: 8px; align-items: baseline; }}
.card b {{ font-size: 1.5rem; }}
.sev {{ display: inline-block; min-width: 2.4em; text-align: center; font-weight: 700; font-size: .8rem; padding: 1px 6px; border-radius: 4px; border: 1px solid currentColor; }}
.sev-S1 {{ color: var(--s1); }} .sev-S2 {{ color: var(--s2); }} .sev-S3 {{ color: var(--s3); }} .sev-S4 {{ color: var(--s4); }} .sev-— {{ color: var(--muted); }}
.filters {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 12px; }}
select, input {{ font: inherit; padding: 4px 8px; border: 1px solid var(--line); border-radius: 6px; background: var(--card); color: var(--fg); }}
table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
td {{ border-top: 1px solid var(--line); padding: 10px 6px; vertical-align: top; overflow-wrap: anywhere; }}
td:first-child {{ width: 56px; }} td.gid {{ width: 56px; color: var(--muted); font-size: .8rem; text-align: right; }}
.title {{ font-weight: 600; }}
.meta {{ font-size: .85rem; margin-top: 2px; }}
.flag {{ background: var(--flag); border-radius: 4px; padding: 0 6px; font-size: .75rem; margin-left: 4px; }}
.flag.warn {{ outline: 1px dashed var(--s2); }}
details summary {{ cursor: pointer; color: var(--muted); font-size: .85rem; margin-top: 4px; }}
details p {{ margin: 6px 0; }}
blockquote {{ margin: 6px 0; padding-left: 10px; border-left: 3px solid var(--line); color: var(--muted); font-style: italic; }}
code {{ font-size: .9em; background: var(--flag); padding: 0 3px; border-radius: 3px; }}
ul.new li {{ margin: 4px 0; }}
tr:target td {{ background: var(--flag); }}
footer {{ margin-top: 40px; font-size: .85rem; }}
</style>
</head>
<body>
<main>
<h1>Angular signal triage</h1>
<p class="muted">{len(issues)} public issues from angular/angular ({repos.get('angular', 0)}), angular/angular-cli ({repos.get('angular-cli', 0)}) and angular/components ({repos.get('components', 0)}), created Oct 12 – Nov 11, 2026, grouped into {len(groups)} issue groups.</p>
<div class="notice"><b>Independent analysis.</b> Not affiliated with or endorsed by the Angular team or Google. Severity calls are an AI agent's reading of public issue text under a published rubric, not the maintainers' priorities. Every call links to its source issue.</div>

<h2>Bug severity</h2>
<div class="cards">{cards}</div>
<p class="muted">Counts are bug, upstream and needs-info groups only. Feature requests, docs and support questions never count toward severity.</p>

<div class="filters">
  <select id="f-sev" aria-label="Severity"><option value="">All severities</option>{''.join(f'<option>{s}</option>' for s in SEV)}</select>
  <select id="f-repo" aria-label="Repository"><option value="">All repos</option><option value="angular">angular</option><option value="angular-cli">angular-cli</option><option value="components">components</option></select>
  <input id="f-q" type="search" placeholder="Filter text" aria-label="Filter text">
</div>
<table id="rated"><tbody>{''.join(row(g) for g in rated)}</tbody></table>

<h2>Not rated <span class="muted">({len(other)})</span></h2>
<p class="muted">{', '.join(f'{v} {k}' for k, v in sorted(cat_counts.items()))}.</p>
<table id="other"><tbody>{''.join(row(g) for g in other)}</tbody></table>
{new_html}
<footer class="muted">
<p>Method: the agent read each issue's title, body and (outside the blind set) comment thread, then grouped and rated it with the rubric in <a href="https://github.com/gonashc/Evidence-linked-engineering-signal-triage-agent/blob/main/docs/rubric.md">docs/rubric.md</a>. Maintainer labels were hidden from it. “From comments” lines summarise public replies; a fix is called verified only when a retest is reported. Quotes are at most 15 words. Reporter usernames are omitted.</p>
<p>Issue text belongs to its authors. Built {e(built)}. Source: <a href="https://github.com/gonashc/Evidence-linked-engineering-signal-triage-agent">repository</a>.</p>
</footer>
</main>
<script>
(function () {{
  var s = document.getElementById('f-sev'), r = document.getElementById('f-repo'), q = document.getElementById('f-q');
  function apply() {{
    var sv = s.value, rv = r.value, qv = q.value.toLowerCase();
    document.querySelectorAll('tbody tr').forEach(function (tr) {{
      var ok = (!sv || tr.dataset.sev === sv) && (!rv || tr.dataset.repo === rv) && (!qv || tr.textContent.toLowerCase().indexOf(qv) !== -1);
      tr.style.display = ok ? '' : 'none';
    }});
  }}
  [s, r, q].forEach(function (el) {{ el.addEventListener('input', apply); }});
}})();
</script>
</body>
</html>
"""
os.makedirs(args.out_dir, exist_ok=True)
with open(os.path.join(args.out_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(page)
print(f"wrote {args.out_dir}/index.html: {len(rated)} rated groups, {len(other)} not rated"
      + (f", {len(new)} awaiting triage" if new is not None else ""))
