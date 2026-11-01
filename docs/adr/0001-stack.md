# ADR-0001 — Stack

**Status:** accepted, 2026-10-30
**Context:** a Claude Code project for personal financial affairs — CRA, lenders, document
packages. Modelled on `ismailkattakath/agentic-nomad`,
which does the same job for travel.

## Decision in one line

**Reuse what is already installed at user scope; this repo declares almost no servers of its
own.** Its value is the rules, the skills and the permissions, not a new stack.

## What this repo uses, and why it beat the alternative

| Job | Chosen | Beat | Why |
|---|---|---|---|
| Read CRA My Account | **Built-in browser pane** (`mcp__Claude_Browser__*`) | page-lab Chromium | CRA's Quartz/Angular app works there, the operator can watch, and a bank's Sign-In Partner session carries through. Measured 2026-10-30: the whole account read in one sitting |
| Read bank portals | **Built-in browser pane** | page-lab Chromium | Same. Canadian bank portals were read there without incident |
| Sites that gate the built-in pane | **page-lab `chrome-devtools` on the operator's Chromium** | — | Wise answers the built-in pane with `Turnstile error: 600010 / WhatsApp works with Google Chrome 100+`-class browser gates. Chromium already holds the session, so there is no login to pass. **Never solve a captcha** |
| WhatsApp | **The operator's Android phone over wireless ADB** (`android-phone` + `mobile-mcp`) | WhatsApp Web | web.whatsapp.com **refuses the built-in pane outright** (browser-version gate), and the phone is where the right account is signed in |
| Mail | **claude.ai Gmail connector** (`ismail@kattakath.com`) | IMAP, browser | Already authorised, structured, searchable |
| Mail with no usable connector (e.g. an organisation's Microsoft 365) | **page-lab Chromium → the web client** | M365 connector | A tenant can block the connector by consent policy; the web client needs nothing granted |
| Documents | **claude.ai Google Drive connector** | browser | Structured search across the whole Drive. Finds a document folder in one query |
| Checklist | **Google Tasks via the `google-workspace-mcp` plugin** | a Markdown list, Workspace Studio | Studio's Tasks step is create-only. Tasks is the operator's existing GTD surface, and `agentic-nomad` already ticks its trip lists this way |
| PDF verification | **poppler** (`pdftotext`, `pdfinfo`, `pdfimages`) | file size, filename | A filename proves nothing. ~53 chars/page means a scan, not text; `pdfimages -list` gives the true resolution |

## Rejected

- **A new `.mcp.json` full of servers.** Everything above is user scope or a plugin the
  operator already enabled. Declaring copies here would create a second pin to drift.
  `.mcp.json` exists but is deliberately empty of servers.
- **An accounting integration** (Plaid, a bank aggregator). The operator reads his own
  accounts; an aggregator means handing a third party every credential in the file.
- **Storing documents in this repo.** See `.gitignore` and CLAUDE.md § Where the data lives.

## Deliberately NOT copied from agentic-nomad

Sibling-project envy is how a second copy gets born. Two things were left out on purpose; a
third (the flake) was later adopted.

| Not copied | Why |
|---|---|
| **`hostpolicy.py` + `hosts.json`** | That allowlist exists to gate where `fill-secret.mjs` may **fill a credential into a page**. This project never fills one — `rules/read-only-banking.md` forbids it and the operator authenticates every portal himself. A host allowlist with no filling to gate is ceremony, and a second copy of the code to drift |
| **`page_scope.py`** | Its matcher is `^mcp__plugin_page-lab_chrome-devtools__.*`. This project's reads go through `mcp__Claude_Browser__*`, so a straight copy would **redact nothing**. Redaction here is a discipline in `rules/identity-data-handling.md`, not a hook — honestly weaker, and recorded as such |

**`flake.nix` — adopted 2026-11-01**, reversing the original "a lockfile for nothing" call.
The operator chose one shape for all three `agentic-*` repos. A public repo's skills shell out
to poppler, python3 and uv; the devShell gives a contributor those without the fleet, and
`toolchain-complete` proves the list resolves. Beancount and Fava are deliberately NOT in it
(ADR-0004's single installer).

**Revisit `page_scope.py`** if this project ever reads a portal through page-lab routinely, or
if the volume of account numbers crossing the transcript makes a mechanical redactor worth
the second copy.
