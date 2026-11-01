# THE GATE — banking is read-only

The agent reads financial portals. It does not act on them.

## Never, on any portal

- **Pay**, **Send Money**, **Transfer**, **Proceed to Pay**, **Make a payment**
- **Set up direct deposit**, change banking details, add or remove an account
- Change **any** account setting, limit, address, contact detail or notification preference
- Accept terms, dismiss a legal notice by agreeing, or enrol in anything
- Open an account, apply for credit, or accept a credit-limit offer

These stay forbidden when the operator asks in passing. If an action is genuinely wanted, he
performs it; the agent can navigate to the screen and stop.

## Credentials

**The agent never types one.** It drives to the login page, says so, and waits. The operator
authenticates — including every two-factor step. Measured 2026-10-30: several portals were read in one
sitting without the agent handling a single password.

**Never solve or bypass a captcha.** A site that gates the built-in pane behind bot detection
is a page-lab Chromium job, where the session already exists (ADR-0001).

## Safe to do without asking

Navigate · read balances, limits, rates, minimums and due dates · open transaction history ·
set a date filter · download a statement the operator asked for · take a screenshot.

## When a portal offers an obvious fix

Report it; do not take it. "The portal shows a *Set up* button for a feature that is off" is
a sentence in the report, not an action. A standing decision the operator has recorded in his
own records in Drive is not re-raised unprompted.
