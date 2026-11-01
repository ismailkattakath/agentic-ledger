---
name: read-lender
description: Read a bank or card issuer at source and capture every figure a debt schedule needs — balance, limit, available credit, rate, minimum, due date. Use when the operator asks to "check my accounts", "update the schedule", "what do I owe", or before any numbers are given to a third party.
argument-hint: "[institution]"
---

# Read a lender at source

Built-in browser pane. The operator signs in. **Read only** — see
`rules/read-only-banking.md`.

## Capture all six, per account

| Field | Why it matters |
|---|---|
| Balance | the obvious one |
| **Credit limit** | a balance means nothing without it |
| **Available credit** | the single most revealing field, and the one most often skipped |
| Interest rate | often stated as Prime + spread |
| **Minimum payment** | this is what goes in monthly obligations |
| **Due date** | a date already passed is the headline |

Where a lender shows both a **current minimum** and a **total minimum**, the gap is
**arrears** — lenders show it this way when earlier minimums were not met. If the due date has also
passed, the whole total is overdue, not just the gap.

## Where each one hides its figures

| Institution | Notes |
|---|---|
| **CIBC** | Account details per product. A loan or mortgage product has its own **View** dropdown of detail pages; **My Documents may list no statements for it** — read its figures from the detail page instead |
| **TD EasyWeb** | Overview then per account. The date-range filter is fragile; three attempts is enough, then state the window you could not reach |
| **Tangerine** | Timeframe dropdown: 30/60/90 days, 12 Months, then per month |
| **Scotiabank** | Sections by product. A section showing a count of zero means no account of that product type exists |
| **Desjardins AccèsD** | A linked **outside** account can appear under "Accounts" with no balance — that is someone else's bank, not Desjardins' |

## Traps

- **A `LN #` on a pre-authorized debit is a servicing reference**, not a separate loan. Match
  it to a line of credit's "Last Payment" before listing it. Counting both double-counts the debt.
- **Direction comes from the running balance**, never a column heading. Text extraction
  renders empty cells as "Not applicable" and misplaces the amount. Check the arithmetic on
  every entry that carries weight.
- **Transfer descriptions mask the counterparty.** `SEND E-TFR ***<ref>` names nobody; open the
  entry. A large one may be a transfer between the account holder's own accounts.
- **Lenders flag stress outside the balance:** zero or negative available credit, an
  over-limit amount due by a stated date, a pre-authorized debit returned unpaid. Read those
  fields every time; none is visible from the balance alone.

## Then

Write limits, rates and minimums to the "Transactions Ledger" Sheet → **Credit terms** tab,
last four digits only, and put "DERIVED" in Rate basis for any figure you computed
(`rules/evidence-at-the-lender.md`). Never type a balance there: its Balance column looks up
the Accounts tab, which `sync-transactions` owns. Totals are formulas — do not add to them.
