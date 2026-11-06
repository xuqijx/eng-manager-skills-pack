---
name: incident-postmortem
description: Write a blameless incident postmortem from the timeline and impact notes the manager supplies. Use when the user asks for a postmortem, incident review, SEV writeup, or outage report.
license: MIT
compatibility: Cursor and Claude agent skills. No network and no extra packages.
metadata:
  author: eng-manager-skills-pack
  version: "1.0.0"
---

# Incident postmortem

Write a blameless review the participants can edit. Describe systems, decisions, and missing safeguards. Do not assign fault to a person.

## When to use

Use this after the notes describe an incident, a drill that caused user-visible pain, or a near miss the manager wants reviewed. Severity is included only when the notes already assign one.

Do not use this skill for a weekly status or a release checklist. Those are `weekly-update` and `release-checklist`.

## Collect before writing

Ask once for anything missing, then draft.

- Title, service, severity if already labeled, document status, window, and timezone
- Impact, including who was affected and whether production served the traffic
- How it was detected, in the notes' words
- Timeline entries in the header timezone, oldest first
- Contributing factors, each marked Confirmed, Hypothesis, or Unknown
- What worked, and where time was lost
- Action items that change a system, a checklist, or a test
- Whether customer identifiers are included

If the user points at `assets/example-input.json`, use that file and keep its fictional banner. Do not invent log lines, ticket ids, or a root cause.

## Rules

- Write "the flag was set to 0 during the drill", not "someone broke staging".
- A hypothesis stays a hypothesis. Do not promote it into the summary.
- Timeline times use the timezone named in the header. Do not convert them unless the notes give the offset.
- Customer names, account ids, and addresses become a count unless the user says this audience can see them.
- Each action names a change to a system, a checklist, or a test, plus an owner and a due date. If the owner is unknown, write `Unassigned` in both the owner and status cells.
- Status is `Draft` until the notes say a review accepted it, `Active` while the incident is still open, or `Final` after acceptance.
- Do not recommend punishment, ranking, or a medical judgment.

## Output

Fill `assets/template.md`.

- Timeline columns are `Time` and `Event`, in the notes' order.
- Contributing-factor columns are `Confidence` and `Statement`. Confidence is `Confirmed`, `Hypothesis`, or `Unknown`.
- Action columns are `Action`, `Owner`, `Due`, and `Status`. Status is `Open`, `Done`, or `Unassigned`.
- An empty section is the single line `Not provided`.

Do not add, rename, or reorder headings. Return the markdown document, not a code fence, unless the user asks.

Add `## Gaps` after the template only when something required is `Not provided`.

## Fictional example

`assets/example-input.json` is a fictional staging incident at Fictional Harbor Labs. It is not a real outage. Keep the disclaimer as the first line, and do not add production impact the file does not state.
