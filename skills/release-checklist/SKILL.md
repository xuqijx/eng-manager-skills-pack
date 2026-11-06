---
name: release-checklist
description: Build a go or no-go release checklist with evidence, rollback, and a watch window. Use when the user asks for a release checklist, launch review, go/no-go, or production rollout plan.
license: MIT
compatibility: Cursor and Claude agent skills. No network and no extra packages.
metadata:
  author: eng-manager-skills-pack
  version: "1.0.0"
---

# Release checklist

Write the go or no-go record for one release window. A check is `Ready` only when the notes contain the evidence.

## When to use

Use this before a production rollout, a staged rollout, or a hotfix. One checklist is one release decision. For several services with separate rollback paths, write one checklist each unless the notes ask for a single combined decision.

Do not use this skill as the incident review. That is `incident-postmortem`.

## Collect before writing

Ask once for anything missing, then draft.

- Release name, environment, owner, and window with timezone
- Scope and explicit non-scope
- Checks covering quality, rollback, observability, support communication, and dependencies
- For each check: status, evidence, and owner
- The decision, and any risk the manager explicitly accepts
- Watch duration, watch owner, and the signals that page someone

If the user points at `assets/example-input.json`, keep its fictional banner. Do not invent a green test, a rollback, or an approval.

## Rules

- Status is `Ready`, `Not ready`, or `Not provided`.
- `Ready` requires evidence that paraphrases the notes. `Not provided` is not evidence.
- Decision is `Go`, `No-go`, or `Not provided`.
- `Go` is allowed when every check is `Ready`.
- `Go` is also allowed when a check is not `Ready` only if `Accepted risk` quotes the manager's explicit acceptance of those named gaps.
- Otherwise write `No-go` and list the gaps in the decision note. Do not soften a missing rollback into `Ready`.
- A hotfix may drop checks the notes say do not apply, but it may not mark a remaining check `Ready` without evidence.
- State the timezone of the window. Do not assume readers share an office.

## Output

Fill `assets/template.md`.

- Check columns are `Check`, `Status`, `Evidence`, and `Owner`.
- The decision line is `Decision: Go`, `Decision: No-go`, or `Decision: Not provided`.
- When no risk is accepted, `Accepted risk` is `None stated.`
- Signals are bullets.
- An empty list is the single line `Not provided`.

Do not add, rename, or reorder headings. Return the markdown document, not a code fence, unless the user asks.

## Fictional example

`assets/example-input.json` is a fictional release at Fictional Harbor Labs. It is not a real launch. Keep the disclaimer as the first line, and do not add approvals the file does not contain.
