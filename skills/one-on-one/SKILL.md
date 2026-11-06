---
name: one-on-one
description: Prepare a 1:1 agenda and split shared notes from private manager notes. Use when the user asks for a one-on-one, 1:1 prep, skip-level notes, or meeting notes with a direct report.
license: MIT
compatibility: Cursor and Claude agent skills. No network and no extra packages.
metadata:
  author: eng-manager-skills-pack
  version: "1.0.0"
---

# 1:1 notes

Write notes the manager can use in the meeting. The report's topics come first. Shared notes and private notes stay in separate sections.

## When to use

Use this before or after a 1:1, a skip-level, or a regular coaching conversation. Set `relationship` from the notes, such as `direct report` or `skip-level`. Do not pretend a skip-level is the person's manager.

Do not use this skill for a team-wide status. That is `weekly-update`.

## Collect before writing

Ask once for anything missing, then draft.

- Report, manager, relationship, date, and duration
- Topics the report raised
- Topics the manager wants to raise
- Feedback as situation, behavior, and impact, and which direction it flows
- The career point the report actually raised
- Shared commitments with owner and date
- Facts that must stay out of the shared note
- Private manager notes

If the user points at `assets/example-input.json`, keep its fictional banner. Do not invent career goals, ratings, or personal details.

## Rules

- Situation is when and where. Behavior is what was observable. Impact is what changed because of it. Do not collapse those into a trait such as "proactive" unless the notes use that word and the three parts are also present.
- Do not write a performance rating unless the notes say this conversation is that rating, and then label it as the manager's rating.
- Do not infer a diagnosis, and do not advise treatment. Keep personal appointments in `Private notes (do not share)` unless the report has agreed to share them. Put the excluded fact in `Shared note excludes` so the shared copy has a reason without the detail when the detail is sensitive.
- A commitment has one owner and a date. A commitment with two owners is two commitments or `Not provided`.
- Do not turn the agenda into a surprise review. Manager topics are listed before the meeting, not added afterward as if they were agreed.

## Output

Fill `assets/template.md`.

- Feedback is one block per item: a `Direction` bullet, then nested `Situation`, `Behavior`, and `Impact` bullets. Direction is `manager to report` or `report to manager`.
- Commitments read `- Owner: action When: date.`
- Empty lists are the single line `Not provided`.

Do not add, rename, or reorder headings. Return the markdown document, not a code fence, unless the user asks.

The private section is for the manager's copy. Say that clearly if you also prepare a version to paste to the report, and omit both the private section and any excluded detail from that version.

## Fictional example

`assets/example-input.json` is a fictional 1:1 at Fictional Harbor Labs. The people are not real. Keep the disclaimer as the first line.
