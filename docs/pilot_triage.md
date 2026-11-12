# Pilot triage, Day 1 (rubric v0.2)

20 reports became 19 issue groups: 4 S1, 5 S2, 7 S3 and 1 S4 bugs, plus 2 non-bugs. Assigned from the issue text only; comment threads not read yet. None of the 25 blind-set issues are included.

| Sev | Issue | Category | What breaks | Why this level | Next check |
| --- | --- | --- | --- | --- | --- |
| S1 | [angular#71825](https://github.com/angular/angular/issues/71825) | Bug · zone.js / SSR | `AsyncLocalStorage` returns another request's data; reporter saw 20 concurrent renders send one user's token | Data leaks between users | Reproduce with 2 concurrent requests and a request-scoped logger |
| S1 | [angular#71618](https://github.com/angular/angular/issues/71618) | Bug · compiler security | SVG `<use href>` bindings skip sanitization | XSS with no app-side workaround | Add `use` to the security schema and a compiler test |
| S1 | [angular-cli#34474](https://github.com/angular/angular-cli/issues/34474) | Bug · SSR build security | Unescaped prerender params run code on the SSR server and inject HTML | RCE from app data; #34569 says the escaping fix shipped in 22.2.5 (not retested) | Confirm fix with the reporter's payloads |
| S1 | [angular-cli#34569](https://github.com/angular/angular-cli/issues/34569) | Bug · SSR build security | A param starting with `\` sends render requests and redirects to another host | SSRF and credential leak at build time | Validate params as same-origin paths |
| S2 | [angular-cli#34674](https://github.com/angular/angular-cli/issues/34674) | Bug · build, regression 22.1 | `main` and `polyfills` bytes change but not their names, so SRI blocks cached scripts | Broke a production app; linked to #34574 | Compute the debug ID before esbuild names files |
| S2 | [angular-cli#34574](https://github.com/angular/angular-cli/issues/34574) | Bug · build, regression 22.1 | Same SRI failure for lazy chunks from the chunk optimizer | Breaks cached production scripts; linked to #34674 | Confirm the #34583 fix covers all optimized chunks |
| S2 | [angular-cli#34452](https://github.com/angular/angular-cli/issues/34452) | Upstream · vite CVE | Vulnerable vite on 22.2, 21 LTS and 20 LTS | Known CVE floor, though only the Windows dev server is exposed | Bump vite on all three branches |
| S2 | [angular#71663](https://github.com/angular/angular/issues/71663) | Bug · angular.dev | Playground fails to start for every tutorial | Learning tool completely down | Check WebContainer rolldown binding |
| S2 | [angular-cli#34312](https://github.com/angular/angular-cli/issues/34312) | Bug · dev server, regression 22.2 | `ng serve` exits with EMFILE on macOS | Core action blocked; capped at S2 (needs `preserveSymlinks` plus over 4,096 directories) | Use @parcel/watcher when following symlinks |
| S3 | [angular-cli#34622](https://github.com/angular/angular-cli/issues/34622) | Bug · ng new / pnpm 11 | `pnpm install` fails after `ng new` | Blocks install, but `pnpm approve-builds` fixes it (workaround rule) | Generate `allowBuilds` in `pnpm-workspace.yaml` |
| S3 | [angular#71409](https://github.com/angular/angular/issues/71409) | Bug · compiler, pre-release | `a--b` gives a misleading "assignment" error; `x = --a` silently changes meaning | Pre-release cap; silent change keeps it above S4 | Review open PR #71410's error text |
| S3 | [angular#71632](https://github.com/angular/angular/issues/71632) | Bug · Signal Forms | One control's parse error shows on every control bound to the field | Wrong validation display in one feature | Scope parse errors per control |
| S3 | [angular-cli#34519](https://github.com/angular/angular-cli/issues/34519) + [angular#71601](https://github.com/angular/angular/issues/71601) | Needs info · HMR / Signal Forms | `useMajorityRatio is not a function`; dev server crashed once | Provisional: no minimal repro | Ask for a StackBlitz repro |
| S3 | [angular#71872](https://github.com/angular/angular/issues/71872) | Bug · hydration | Hydration rewrites attributes, restarting autoplay videos | Degraded UX and extra DOM writes | Skip unchanged attribute writes on hydrated nodes |
| S3 | [angular#71953](https://github.com/angular/angular/issues/71953) | Bug · HttpClient | A synchronously throwing interceptor leaves the app never stable | Shown in a test only; could hang SSR (unverified) | Check whether SSR render waits forever |
| S3 | [angular#71917](https://github.com/angular/angular/issues/71917) | Bug · SSR transfer cache | Blob responses hydrate as an empty 0-byte Blob | Wrong data; workaround: exclude from cache | Serialize Blob bodies before caching |
| S4 | [angular#71562](https://github.com/angular/angular/issues/71562) | Bug · angular.dev | `GEMINI.md` asset returns 404 | One missing asset, no detail given | Confirm the asset path still exists |
| — | [angular#71399](https://github.com/angular/angular/issues/71399) | Feature request | Custom JSON parser for HttpClient | Not a bug | Product feedback list |
| — | [angular#71796](https://github.com/angular/angular/issues/71796) | Docs | Two-way binding guide lacks `model()` input/output detail | Not a bug | Docs backlog |

## Grouping calls

| Reports | Call |
| --- | --- |
| angular-cli#34574 + #34674 | Linked, not merged: same root cause, two fixes |
| angular-cli#34519 + angular#71601 | Merged: same project, same error; needs info |
| angular-cli#34474 + #34569 | Linked, not merged: two separate security flaws |
