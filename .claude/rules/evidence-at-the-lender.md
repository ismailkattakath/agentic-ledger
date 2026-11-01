# Every figure comes from the lender's own screen

A number in an email, a statement, a previous session's summary or an agent's memory is a
**lead**. The figure that goes in a schedule is the one read today on the institution's own
page.

A schedule compiled from old leads drifts: balances move, and whole institutions can be
missing, not just accounts. Figures live in the data folder, not here.

## Per account, capture all six

Balance · credit limit · available credit · interest rate · minimum payment · due date.

Available credit is the one most often skipped and most often decisive: an account can show
**$0.00 or negative available** while its balance looks ordinary — which no balance figure
reveals.

## Label what you derived

An interest rate computed from a charge is **derived**, not stated. Say so, and give the
arithmetic:

> A month's interest charge divided by the average balance, annualised, gives a rate the
> lender never published. Write it as *"≈X% a year, derived from the charge"* — never as
> the lender's rate.

A judgement call is labelled as one: *"Available credit near zero while the balance sits well
under the published limit can mean the lender lowered the limit. Lenders rarely say so; confirm
it."*

## Read direction from the running balance, never a column heading

A transaction list that renders "Not applicable" in the empty column will be parsed wrongly
by text extraction about half the time. Check the arithmetic: if the balance moves
−$2,000.00 → −$500.00, a $1,500.00 entry is a **credit**, whatever column it appeared in.
Do this for every entry that carries weight.

## Traps measured on real portals

| Trap | Reality |
|---|---|
| A `LN #` reference on a pre-authorized debit | A **servicing reference for an existing line of credit**, not a separate loan. Match it to a line of credit's "Last Payment" before listing it. Counting both double-counts the debt |
| A date-range filter that rejects valid dates | Three attempts is enough. Say the window you could not reach rather than implying you checked it |
| A 12-month view whose oldest row is 4 months old | The view is not the history. State the range you actually saw |
