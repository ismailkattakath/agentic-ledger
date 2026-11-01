# No data here — this repo holds procedures; every fact lives in a Google app

Neither this repo nor its sibling `agentic-nomad` ever holds data.

**The test:** would this line read the same for a different person? Yes → procedure, it may
live here. No → data, it goes to its ONE Google home, never to a repo file.

| Fact | Its one home |
|---|---|
| Live status, what is held, verified or sent, due dates | the matter's Google Tasks list |
| Balances, schedules, documents, write-ups | the Drive data folders in `CLAUDE.md` § Where the data lives |
| Timed commitments | Google Calendar |
| Transactions and balances, per account | the **derived journal**, `$LEDGER_DRIVE_DIR/Ledger/main.beancount`, rebuilt from the statement files (ADR-0004). Never edited, so it holds no fact of its own |
| Category rules and per-transaction decisions | the Sheet tabs "Category rules" and "Review decisions" — never the journal, which is rebuilt from them (ADR-0004) |

The job → app mapping is the `workspace-gtd` plugin; do not restate it. **Before writing a
fact anywhere, check it is not already in its home** — a second copy is a bug. A worked
example uses fabricated values (as `identity-data-handling.md` does for a SIN), never real ones.
`.gitleaks.toml` is the mechanical floor; it catches numbers, not prose — this rule is the rest.
