# ADR-0002 — Operating model

**Status:** accepted, 2026-10-30. Live status is not kept in this repo — see § Status.

## Status

Live state — what is read, held, verified or sent — lives in the matter's Google Tasks
list, and figures live in the Drive data folder named in `CLAUDE.md`.
This repo keeps no copy (`rules/no-data-here.md`).

## The four layers, and the gate

| Layer | How | Can act outward? |
|---|---|---|
| **READ** | CRA and bank portals in the built-in browser pane · Gmail and Drive connectors · the operator's Android phone over ADB for WhatsApp · web mail with no connector via page-lab Chromium | No |
| **RECORD** | The Google Drive data folder named in CLAUDE.md (schedule, package inventory, write-ups) + Google Tasks | No |
| **ASSEMBLE** | PDFs verified by text extraction, named `NN-topic-detail.pdf`, staged in the data folder | No |
| **SEND** | A verified recipient's secure portal · Gmail connector, draft-first · WhatsApp from the phone | **Yes**, operator-decided |
| **GATE** | **Banking is read-only.** No payment, transfer, enrolment or settings change on any portal — `rules/read-only-banking.md` | — |

The gate protects against the agent moving money while reading an account. Sending is not
gated by a rule because the agent never sends on its own: every send is the operator's
decision (§ Division of labour).

## Division of labour

**The agent runs unattended** through READ, RECORD and ASSEMBLE. No "shall I continue?" for a
routine read, a document download the operator asked for, or a file write inside the data
folder.

**The operator authenticates.** Every portal sign-in is his; the agent drives the browser to
the login page and stops. The agent never types a credential (`rules/read-only-banking.md`).

**The operator decides anything outward.** Sending a document, replying to a correspondent, paying
an amount.

## Where records live — decided 2026-10-30, REVISED 2026-10-31

**Revised 2026-10-31:** data lives in the Google app that fits it, with no second copy.
Plain `.md` files in Drive are not a Google app. Account figures go into the
"Transactions Ledger" Sheet (ADR-0003), which already holds balances and transactions; the
write-ups become one Doc. Superseded files go to an archive folder in Drive.

| Fact | Its one home |
|---|---|
| Status, actions, due dates | the matter's Tasks list |
| Balances, bank transactions | "Transactions Ledger" → Accounts, Transactions (ADR-0003) |
| Limits, rates, minimums, loan terms | "Transactions Ledger" → Credit terms. Balance is a lookup into Accounts, never typed |
| Income versus obligations | "Transactions Ledger" → Affordability, formulas only |
| Request, inventory, sending rules, analysis | the matter's package Doc, in the data folder |
| The documents | the PDFs in the data folder |

**The 2026-10-30 objection is answered, not ignored.** It said a Sheet would lose the
"derived, not stated" annotations. Credit terms keeps them in a **Rate basis** column and a
Notes column, and the matter's Doc explains what the figures mean.

Rejected: a Markdown schedule file (balances AND due dates: a second copy of the Ledger and
of the dated Tasks), and a separate schedule Sheet (it duplicates the Ledger's balances and
transactions, and drifts).

## What this project does NOT do

- **It does not move money.** Not a payment, not a transfer, not a direct-deposit enrolment.
- **It does not give financial advice.** It reads accounts, assembles documents, states
  arithmetic. Any financial decision is the operator's call, with a licensed professional
  where one is needed.
- **It does not hold the documents.** They live in the data folder; this repo holds the
  procedures for producing and checking them.
