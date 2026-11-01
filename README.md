# agentic-ledger

Personal financial affairs, run from Claude Code — CRA, lenders, document packages, the
checklist. Sibling of [`agentic-nomad`](https://github.com/ismailkattakath/agentic-nomad),
which does the same for travel.

**This repository holds procedures. It holds no documents, balances or account numbers.**
Those live in the operator's Google Drive, in the folders named in `CLAUDE.md`.

## Start here

| Read | For |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | the architecture, the gate, and where the data actually lives |
| [`docs/adr/0001-stack.md`](docs/adr/0001-stack.md) | every tool choice and what it beat — including what was deliberately **not** copied from agentic-nomad |
| [`docs/adr/0002-operating-model.md`](docs/adr/0002-operating-model.md) | the operating model; live status is the Tasks list |

## The gate

**Banking is read-only.** No payment, transfer or settings change on any portal. The
operator authenticates every sign-in; the agent never types a credential. Anything outward —
sending a document, replying, paying — is the operator's decision.

## Skills

| Skill | Does |
|---|---|
| `read-cra-account` | reads CRA My Account end to end, downloads notices, knows the navigation traps |
| `read-lender` | captures all six figures per account at the institution's own screen |
| `verify-package-document` | proves a PDF before it counts as held |
| `tick-checklist` | ticks Google Tasks from hard evidence, never from intent |

## Rules

`no-data-here` · `read-only-banking` · `identity-data-handling` ·
`evidence-at-the-lender` · `untrusted-content`

Read the directory; they are short and each one is there because something went wrong once.
