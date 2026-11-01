---
name: read-cra-account
description: Read CRA My Account end to end — assessments, balances, benefits, profile, mail — and download notices as PDFs. Use when the operator asks "has the NOA arrived", "what does CRA say", "check my CRA account", or before any filing or document package that needs a Notice of Assessment.
argument-hint: "[what to look for]"
---

# Read CRA My Account

Built-in browser pane only. The operator signs in; sign-in partner sessions (TD, etc.) carry
straight through to the account.

## Sign in

`https://www.canada.ca/en/revenue-agency/services/e-services/cra-login-services.html` →
**Sign-In Partner** → the bank → the operator authenticates. If a session already exists the
bank step is invisible and the Welcome page appears directly.

## ⚑ The navigation trap, measured 2026-10-30

Correspondence links look reusable:
`#/ind/communications/ricc-view/<base64ish>/08`. **The token is minted per render.**

- Reusing one from a few minutes earlier → **CC-460** "Could not display this correspondence
  item"
- That failure poisons the SPA → the **next** route gives **CC-571** "You are not authorized
  to view this page"
- The same notice, re-opened from a fresh Overview, has a completely different token

**Recovery:** navigate to `#/spoe`, click the account, then reach everything by clicking
in-app links. Plain section routes survive direct navigation fine —
`#/ind/ident/personal-profile`, `#/ind/benefits/benefits-summary`, `#/ind/returns/tax-returns`,
`#/cus/soa`. Only correspondence tokens do not.

## The sweep, in this order

| # | Where | What it answers |
|---|---|---|
| 1 | Overview | assessment dates, income tax balance, next benefit payments |
| 2 | **Mail** | every notice. Opening one marks it read — say so |
| 3 | Tax returns | filing history, NETFILE access code, direct deposit state |
| 4 | **Profile** | address, phone, direct deposit, marital status, children, authorized representatives |
| 5 | Benefits and credits | benefit balances and status |
| 6 | Accounts and payments → **Statement of account** | the per-account ledger. A dropdown: Income tax, then one entry per benefit program on the account |
| 7 | Uncashed cheques | money never collected |
| 8 | Savings and pension plans | RRSP and TFSA room, HBP, FHSA, LLP |
| 9 | Carryover amounts | unused capital losses, tuition, training credit |
| 10 | Tax information slips | per year. **An empty slip dropdown is a finding**, but prove the control works by selecting a year that does have slips |

## Downloading a notice

Each notice view carries a **PDF** button that writes straight to `~/Downloads` with a
generated name. **No Open/Save dialog** — none of the macOS file-panel difficulty applies.

Then verify (`verify-package-document`) and rename. Check each PDF for a full SIN
(`rules/identity-data-handling.md`); do not assume a notice type masks it.

## What CRA will not tell you

- **No login or activity history exists.** Security settings holds only multi-factor options
  and the PIN.
