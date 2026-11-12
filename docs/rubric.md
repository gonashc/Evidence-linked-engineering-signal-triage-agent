# Severity rubric and grouping rules (v0.2, approved Nov 12, 2026)

## Severity (bugs only, per issue group)

| Level | Meaning for a framework or tooling issue |
| --- | --- |
| S1 Critical | Exploitable security flaw in apps built with it (XSS, RCE, SSRF, data leaking between users), silent data corruption, or a production outage across many apps |
| S2 High | Blocks a core action (install, build, serve, render) or breaks apps already in production, with no simple workaround; also a known CVE in a dependency, or an interactive learning tool (such as the Playground) that is completely down |
| S3 Medium | Wrong behaviour in one feature, an edge case, a performance cost, or a block that has a simple documented workaround |
| S4 Low | Misleading error message, cosmetic or layout issue, a single broken docs page or asset |

Adjustments, applied in order:

1. **Known CVE floor.** A published CVE in a dependency is at least S2, even when only the dev server is exposed, because security scanners fail builds.
2. **Reach.** A crash that needs an opt-in setting plus a specific OS stays at S2 at most.
3. **Workaround.** A simple workaround that the error message itself points to drops the issue one level.
4. **Release channel.** A regression only in a pre-release (`-next`, `-rc`) is never above S3.
5. **Evidence.** No repro and no error text means **needs info**; severity is provisional and flagged.

Each call gives a one-sentence rationale and one next engineering check.

## Categories

Bug, feature request, docs, support question, needs info, upstream (the cause is in a dependency). Only bugs get a severity.

## Grouping

- **Merge** when reports share the same symptom, the same root cause and the same fix. Keep every report's link on the group.
- **Link, don't merge** a follow-up that needs a different fix (even with the same root cause), or the same failure pattern in a different component.
- **Split** one issue that describes two independent failures into two records.
- **Never merge on title similarity alone.** Keep ambiguous pairs separate and flag them.

## Decision log

| Date | Decision | Effect on pilot |
| --- | --- | --- |
| 2026-11-12 | Known dependency CVEs are S2, even if only the dev server is exposed | angular-cli#34452: S3 to S2 |
| 2026-11-12 | A one-command workaround named in the error drops one level | angular-cli#34622 stays S3 |
| 2026-11-12 | A learning tool on the docs site that is completely down is S2 | angular#71663: S4 to S2 |
| 2026-11-12 | Same root cause with two fixes = linked groups, not merged | angular-cli#34574 and #34674 are two S2 groups |
