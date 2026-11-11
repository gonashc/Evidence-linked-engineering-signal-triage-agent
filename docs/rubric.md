# Severity rubric and grouping rules (DRAFT v0.1, Day 1)

Status: draft, four open decisions at the end. Not yet approved.

## Severity (bugs only, per issue group)

| Level | Meaning for a framework or tooling issue |
| --- | --- |
| S1 Critical | Exploitable security flaw in apps built with it (XSS, RCE, SSRF, data leaking between users), silent data corruption, or a production outage across many apps |
| S2 High | Blocks a core action (install, build, serve, render) or breaks apps already in production, with no simple workaround |
| S3 Medium | Wrong behaviour in one feature, an edge case, a performance cost, or a block that has a simple documented workaround |
| S4 Low | Misleading error message, cosmetic or layout issue, broken docs-site page |

Adjustments, applied in order:

1. **Reach.** A crash that needs an opt-in setting plus a specific OS stays at S2 at most.
2. **Workaround.** A simple workaround that the error message itself points to drops the issue one level.
3. **Release channel.** A regression only in a pre-release (`-next`, `-rc`) is never above S3.
4. **Evidence.** No repro and no error text means **needs info**; severity is provisional and flagged.

Each call gives a one-sentence rationale and one next engineering check.

## Categories

Bug, feature request, docs, support question, needs info, upstream (the cause is in a dependency). Only bugs get a severity.

## Grouping

- **Merge** when reports share the same user action, environment and outcome, and the same root cause. Keep every report's link on the group.
- **Link, don't merge** a follow-up that needs a different fix, or the same failure pattern in a different component.
- **Split** one issue that describes two independent failures into two records.
- **Never merge on title similarity alone.** Keep ambiguous pairs separate and flag them.

## Open decisions

1. Dev-only dependency vulnerabilities: S3 (only the dev server is exposed) or S2 (scanners fail builds)?
2. Does a one-command workaround named in the error message drop S2 to S3?
3. Should a fully broken learning tool on the docs site count as S2 rather than S4?
4. Merge reports with one root cause but two separate fixes, or keep them as linked groups?
