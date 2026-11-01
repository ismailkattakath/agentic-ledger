# ADR-0004 — Double-entry journal, derived

**Status:** accepted, 2026-11-01, when the cutover gate passed (results in Tasks).
Supersedes the "Sheet is the ledger" part of ADR-0003; the export-first sourcing stays.

## Decision in one line

**Transactions and balances live in a Beancount journal that is a build artifact**: rebuilt
from the statement files in Drive plus human decisions held in Google-native Sheet tabs.
Nobody edits the journal by hand. Fava shows it, read-only, on demand.

## The pieces and their one home

| Fact | Home | Edited by |
|---|---|---|
| Statement files (QFX, CSV, PDF) | Drive, `$LEDGER_DRIVE_DIR/Statements/` | Downloaded, never edited |
| Canonical rows | Drive, ledger `cache/<sha256>.jsonl` (statement-extract output) | Regenerated |
| Category rules | Sheet tab "Category rules" | Operator |
| Per-transaction decisions (override, note, payment-service link, accepted suggestion) | Sheet tab "Review decisions", keyed by Key | Operator |
| Account map, transfer settings | Drive, `ledger.toml` (marked Keep forever on change) | Operator, rarely |
| The journal | Drive, `$LEDGER_DRIVE_DIR/Ledger/` | **The build only** |
| Procedures | This repo | — |
| Generic build code | The `beancount` plugin in `kattakath/skills` | — |

## Why derived, not hand-kept

- **Drive keeps ~30 days / 100 versions of a non-Google file** unless a version is marked Keep
  forever ([Google](https://support.google.com/drive/answer/2409045)). A journal holding
  hand-made decisions could lose them to a bad edit noticed late.
- A derived journal holds **no fact of its own**. Every input is durable: statements never
  change, and decisions sit in Sheets, which keep their own history.
- **Rebuild is idempotent.** A bad build is discarded: `bean-check` must exit 0 before the file
  is written.
- The repo stays data-free, which the operator requires because it may go public.

## What it beat

| Option | Why it lost |
|---|---|
| Keep the Sheet as the ledger | No double-entry, no balance assertions, no net worth; transfer pairing is a bolt-on script |
| Hand-kept journal (classic Beancount) | Decisions live only in a file with ~30-day version history |
| hledger | Equally sound; Beancount has Fava (MIT, budgets, query UI) and the beangulp importer interface |
| GnuCash | GUI-first, binary/SQL book; no text diff, poor agent fit |
| Actual / Firefly III | A server plus a database: a second home for the same facts |
| Always-on Fava (launchd) | Nothing needs it between reviews; on demand costs nothing idle |
| Pinned uv environment | The tools are wanted on PATH everywhere; nix-config is the existing installer |

## Transfers

- Own-account legs pair at build time with the algorithm proven in the retired `categorize.py`
  (exact, Wise fee band, FX band, in-wallet conversion; greedy one-to-one). The cutover proved
  the port pair-for-pair against it.
- **A paired leg clears through `Assets:Transfers`, which always nets to zero. An unpaired leg
  posts to `Equity:Transfers:External`** and the build lists it (decided 2026-11-01). The
  rejected alternative, leaving unpaired legs in the clearing account, carried them in net worth
  as phantom assets and debts. Most have no possible partner: the other account's history
  starts later. A full rebuild re-pairs every time, so a late partner moves its leg back.
- Unpaired legs whose partner account *is* covered go to Review decisions with a note.

## Statement assertions that a day cannot separate

A bank can print next period's fee dated this period's last day. The figure then cannot be
asserted at day granularity. The build sets such an assertion aside and lists it; it never
adjusts the figure. On a PDF-statement account this can affect many closings.

## Weakest assumption

That Google Sheets keeps version history long enough for the decision tabs. Google publishes
no fixed retention for Sheets. The current decisions are always present; only old undo steps
can age out.
