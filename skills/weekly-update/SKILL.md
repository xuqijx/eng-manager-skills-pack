---
name: weekly-update
description: Draft a one-page weekly engineering update from the manager's notes for partners outside the team. Use when the user asks for a weekly update, Friday status, stakeholder digest, exec note, or engineering status report.
license: MIT
compatibility: Cursor and Claude agent skills. No network and no extra packages.
metadata:
  author: eng-manager-skills-pack
  version: "1.0.0"
---

# Weekly update

Write the update the manager can forward. Do not wrap it in advice unless they ask for a critique.

## When to use

Use this for a recurring update to people outside the working group: product, support, a director, or a partner team. Name the timezone. Spell out an acronym the first time the wider audience would not know it.

Do not use this skill for an incident review, a 1:1, or a release decision. Use `incident-postmortem`, `one-on-one`, or `release-checklist`.

## Collect before writing

Ask once for anything missing, then draft.

- Team, organization, period, timezone, audience, and author
- One headline that states the conclusion
- Shipped work, including which environment it reached
- Work still in progress, with an owner when the notes name one
- Risks, each with an ask or an owner
- Metrics, each with a number, a window, and a source
- Next week's commitments
- Notes that must not be forwarded

If the user points at `assets/example-input.json`, use that file. If they have no notes and do not ask for the fictional example, ask for notes. Do not invent a company, a metric, a date, or a person.

## Rules

- The headline is the conclusion. "Weekly update" is not a headline.
- Shipped means the notes say it reached the environment the audience cares about. A change that is only in staging stays in progress for a production audience, or the bullet names staging.
- Do not include performance feedback about a person. That belongs in `one-on-one`.
- Every risk has an ask, an owner, or both. If neither is known, write `Ask: Not provided`.
- Omit a metric that lacks a number, a window, or a source. Never estimate a number, and never describe a dashboard you did not see in the notes.
- Keep the forwardable portion under about 400 words. Put uncertainty in `Manager notes (do not forward)`.
- Write the document in the language of the notes. Keep the template headings in English unless the user asks to translate them.
- Use an identifier only when it appears in the notes.

## Output

Fill `assets/template.md`. Replace every `{{placeholder}}` from the notes. Render each list as bullets, one fact per bullet. An empty list is the single line `Not provided`.

Do not add, rename, or reorder headings. Return the markdown document itself, not a code fence, unless the user asks for a fence.

Add a final `## Gaps` section only when a field is `Not provided` or a metric was omitted. If nothing is missing, stop at the template.

## Fictional example

`assets/example-input.json` is a fictional dry run for Fictional Harbor Labs. It is not a real team, metric, or person. When you use it, the disclaimer stays the first line.

Read that file and fill `assets/template.md`. Do not add revenue, headcount, or incidents that the file does not contain.
