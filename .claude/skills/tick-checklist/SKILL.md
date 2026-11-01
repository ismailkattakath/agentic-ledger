---
name: tick-checklist
description: Strike off tasks in the financial checklist in Google Tasks (one list per matter) from hard evidence — a verified file in the data folder, a lender screen read today, or an official confirmation. Use when the operator asks "what can I tick off", after a document lands, or after a payment clears.
argument-hint: "[task list name]"
---

# Tick the checklist — from hard evidence only

The agent completes a task on its own **when the evidence bar below is met**, and reports
what it ticked. Same standard as `agentic-nomad`'s skill of this name (decided 2026-10-27,
superseding propose-only).

The guard is the evidence bar, not a yes. **A wrong tick silently hides an obligation**, and
in this project an obligation is a due date with a fee behind it.

## Where things are

| What | Tool |
|---|---|
| Checklist | Google Tasks via the `google-workspace-mcp` plugin's Tasks tools |
| Documents | the data folder named in CLAUDE.md |
| Lender figures | the institution's own screen, read today (`read-lender`) |
| Confirmations | the Gmail connector (`ismail@kattakath.com`) |

## The evidence bar

| Task type | Ticks only when |
|---|---|
| **A document is held** | the file is in the data folder **and** has passed `verify-package-document` — page count, real text or an expected scan, no stray placeholders |
| **A figure is captured** | read **at the lender** today and written to "Transactions Ledger" → Credit terms, with derived values labelled |
| **A payment is made** | it appears **on the account**, not in an email and not because the operator said he would |
| **A document was sent** | it appears in **Sent Items**, or the chat shows it delivered |
| **A question is answered** | the operator answered it, or a primary source did |

## Never ticks on

A filename · a file size · an email saying something was sent · a previous session's summary ·
an intention · a screenshot of a form before it was submitted.

## Notes carry the evidence

Every tick writes **why** into the task note: the filename and page count, the screen and the
date, or the message and its timestamp. A tick with no note is not auditable, and six weeks
later nobody can tell a real one from a hopeful one.

Keep a decision's attribution and date in the note too — `(operator, 2026-10-30)` — so a
later session knows it was settled rather than assumed.

## Retiring a list

Prefix with `Archive · ` rather than deleting. The evidence trail outlives the matter.
