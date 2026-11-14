# LinkedIn post (draft)

I built an AI triage agent in 3 days and scored it against Angular's maintainers and against me. It agreed with the maintainers more often than I did.

The setup: a month of public GitHub issues from angular/angular, angular/angular-cli and angular/components (Oct 12 – Nov 11, 2026). 163 issues, pull requests excluded. The agent groups duplicates, rates each bug S1–S4 against a written rubric, gives a one-line reason and a next engineering check, and links every call to the issue it came from.

What it produced:
• 163 issues → 161 issue groups
• 5 S1, 17 S2, 84 S3, 13 S4 bugs
• 42 feature requests, docs and support questions, kept out of the severity totals

How I kept the accuracy check honest:
• The maintainers' labels, state and close reasons sat in a folder the agent was blocked from reading, enforced in its tool permissions and not just in the instructions.
• For 25 issues held out as a blind set, the agent saw only what I saw: title and body. I labelled them myself first.
• The agent's 25 calls were committed to git before any scoring ran, so they can't have been tuned to the answers.

Results on the blind set:
• Agent vs. maintainers: 74% exact severity, 100% within one level
• Me vs. maintainers: 60% exact, 100% within one level
• Agent vs. me: 63% exact, 89% within one level, 92% agreement on what is a bug at all

Where we disagreed: the agent rated higher than the maintainers 4 times out of 5. Its two S2 calls, keyboard activation being swallowed inside an accordion and clicks ignored on older iOS, are both accessibility or reach problems that a priority label doesn't reward. I rated lower than both, putting 7 issues at S4 where the agent put 2.

Caveats, because they matter:
• It's a small sample (19–20 comparable calls).
• A maintainer priority label isn't a severity rating. I mapped P0→S1, P1→S2, P2–P3→S3 and P4–P5→S4, and that mapping is a judgement call.
• Most maintainer labels carry no type, so category agreement with them rests on 5 issues.

What I'd take from it: the agent is good at the boring 80%. It extracts the evidence, applies the rubric the same way every time and never loses a link. The value of a human is in arguing about the rubric, not in applying it.

The dashboard refreshes weekly: https://gonashc.github.io/Evidence-linked-engineering-signal-triage-agent/
Code, rubric and data: https://github.com/gonashc/Evidence-linked-engineering-signal-triage-agent

Built from lab A11 of The Gen Academy "AI-Native Power User Workbook", with public GitHub issues standing in for a private Slack channel.

Independent analysis, not affiliated with or endorsed by the Angular team or Google.
