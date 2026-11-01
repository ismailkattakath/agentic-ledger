# ADR-0003 — Transaction ledger

**Status:** accepted, 2026-10-31; the Sheet-as-ledger part was **superseded by ADR-0004** on
2026-11-01 (derived Beancount journal; the Transactions tab is archived). Export-first
sourcing stands.

## Decision in one line

**Every account's transactions land in one Google Sheet, "Transactions Ledger", from the
lender's own QFX/OFX export, downloaded while the operator is signed in.** No aggregator.
Revisit when Canadian open banking goes live.

## What it beat

| Option | Credentials leave him? | Canadian coverage | Verdict |
|---|---|---|---|
| **Lender's QFX/OFX export, agent downloads** | **No** | Any portal with an export | **Chosen** |
| Aggregator (Tiller, Monarch, Plaid, Flinks) | **Yes**, to a third party | Patchy. Tiller's FAQ: "US-based banks only"; its forum shows TD down for about two months and CIBC needing frequent reconnects | Rejected. ADR-0001 already rejected aggregators on credential grounds; nothing here changes that |
| Canadian consumer-driven banking (open banking) | No, token-based and accredited | Big six banks must take part | **Not live**, with no firm date as of 2026. It removes the credential objection; **switch to it when it ships** |
| PDF statements | No | Everyone | Fallback for history older than the export window. Text extraction misreads direction (`rules/evidence-at-the-lender.md`) |
| CSV export | No | Wide | No FITID, so dedupe needs a made-up key that breaks when the bank edits a description. Second choice, per institution, only when QFX is absent |

## Why QFX/OFX

- **FITID** is the bank's own transaction id, unique per account (OFX spec). It gives a dedupe
  key for free, so overlapping windows are harmless.
- **Sign is defined by the spec** (negative = money out, from the holder's view) instead of
  inferred from a column heading.
- The parser is **`ofxtools`**, off the shelf, pinned in the script's inline metadata and run
  by `uv run --script`. `uv` is already on PATH.
- **This supersedes ADR-0001's "there is no code here"** reason for having no flake. The repo
  now holds one script. It still has no flake, but for a new reason: the script's inline
  pin is its whole toolchain. A flake would be a second pin for the same dependency.
  Revisit if a second script or a test suite arrives.

## An export is the lender's own data, not a statement

`rules/evidence-at-the-lender.md` treats a statement as a lead. An export downloaded from the
portal today is the lender's own record, so transactions may be taken from it. **Balances
still come from the screen.** The skill reconciles the two (opening + rows = closing) before
a sync counts.

## Where things live

| What | Home |
|---|---|
| Transactions, account sync state, monthly pivot | The "Transactions Ledger" Sheet, in `$LEDGER_DRIVE_DIR` |
| Raw export files | `$LEDGER_DRIVE_DIR/Statements/<Institution>/`. **They carry the full account number** |
| Procedure and parser | `.claude/skills/sync-transactions/` |

## Weakest assumption

That each of the operator's institutions offers QFX/OFX. This is unverified per bank. The
first sync of each one settles it, and its Accounts row records the format found.
