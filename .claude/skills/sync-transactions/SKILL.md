---
name: sync-transactions
description: Pull every bank and card account's transactions into the derived Beancount journal from the lender's own QFX/OFX, CSV or PDF export — export, extract, build, check, review in Fava — with last-four masking and Key dedupe. Use when the operator asks to "sync my transactions", "update the ledger", "backfill <bank>", "rebuild the journal", "what did I spend on X", or before any budget or spending review.
argument-hint: "[institution] [from YYYY-MM-DD]"
---

# Sync transactions into the journal

**The journal is a build artifact. Nobody edits it.** It is rebuilt in full from durable
inputs on every sync, and written only when Beancount's own check passes. Why:
`docs/adr/0004-double-entry-journal.md`. Why exports and not an aggregator:
`docs/adr/0003-transaction-ledger.md`.

## Where each input lives — all outside this repo

| Input | Home (under `$LEDGER_DRIVE_DIR`, the finance folder in Drive) | Edited by |
|---|---|---|
| Statement files (QFX/OFX, CSV, PDF) | `Statements/<Institution>/` — they carry full account numbers | downloaded, never edited |
| Canonical rows, one file per statement | `Ledger/cache/<sha256>.jsonl` | statement-extract |
| Account map, transfer settings, FX bands, gaps | `Ledger/ledger.toml` — mark each change **Keep forever** in Drive | operator, rarely |
| Exchange rates (`price` lines) | `Ledger/prices/*.beancount` — pricehist output, refreshed each sync | `pricehist` |
| Assets no statement covers, currency pegs | `Ledger/ledger.toml` `[[snapshot]]`, `[pegs]` | operator, yearly |
| Screen balances, last-four overrides | `statement-extract/accounts.toml` | operator |
| Category rules | Sheet "Transactions Ledger" → tab **Category rules** | operator |
| Per-transaction decisions (category, note, service link) | same Sheet → tab **Review decisions**, one row per Key | operator |
| **The journal** | `Ledger/main.beancount`, reached as `$BEANCOUNT_JOURNAL` (`~/.local/share/ledger` is a symlink to `Ledger/`) | **the build only** |

Find the Sheet by title with the Drive connector; never write its ID into this repo. The
tabs Transactions, Accounts, Monthly and Source details are **archived** (ADR-0004): read
them for history, never write them.

## Steps

1. **Ask the journal where each account stands:** the `query` skill's balance recipe, or
   the last `balance` directive per account. A new account starts at the oldest date the
   portal offers; say what that date was.
2. **Built-in browser pane, operator signs in** (`rules/read-only-banking.md`). Download
   **QFX/OFX** where offered (TD may call it *Quicken*), otherwise the CSV or PDF named in
   § Per institution. Overlap the last sync by 7 days: the Key dedupes it.
3. **Move the file into Drive at once:** `Statements/<Institution>/`. It never stays in
   `~/Downloads`, never enters this repo (`.gitignore` blocks the formats as a backstop), and
   is never `cat`'d into the transcript.
4. **Extract into the cache**, one JSONL per file, named by the file's sha256:

   ```bash
   FIN="${LEDGER_DRIVE_DIR:?set it to the finance folder in Drive}"
   SE="$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.claude/plugins/installed_plugins.json")))["plugins"]["statement-extract@kattakath"][0]["installPath"])')/scripts/statement-extract"
   # The run log records reconcile checks WITH figures: keep it in the data folder.
   export STATEMENT_EXTRACT_LOG="$FIN/statement-extract/runs.jsonl"
   python3 -I "$SE" extract "<file>" --accounts "$FIN/statement-extract/accounts.toml" \
     > "$FIN/Ledger/cache/$(shasum -a 256 "<file>" | cut -c1-64).jsonl"
   ```

   - **Extract every statement file, overlapping or not.** There's no need to remember what
     was synced. A file already in `cache/` has the same sha256 name, so skip it. The build
     owns each day (the `beancount:build` skill, § survivorship):
     - a QFX/CSV outranks a PDF for the days both cover;
     - a PDF fills only the days nothing better covers;
     - a hole gets a labelled `Equity:Gaps` pad.
   - **Read the report's `overlap:` and `gap bridged:` lines.** A new bridge is history never
     fetched. Download it if the portal still offers it.
   - **A reissued credit card** (expiry, loss, theft) gets a new number but stays the same
     card account at every bank. Its old statements print the old
     number, and the extract refuses them (`header_last4`). Add an `accounts.toml` entry
     mapping the old number (`acctid_last4`) to the current one (`last4`), with
     `reissued = true`. Its rows then key to the current card account.
   - **Exits 3, 4 or 5 are refusals: never work around them.** Hand the report to the
     plugin's `statement-extract:adapter-author` agent.
   - **stdout carries figures.** Redirect it; never print it.
5. **Refresh exchange rates** (Bank of Canada, public, no sign-in), once per foreign currency
   held: from the day after the last line in `Ledger/prices/<cur>-cad.beancount` to today,
   appended to that file:

   ```bash
   pricehist fetch bankofcanada <CUR>/CAD -s <day after last line> -o beancount >> "$FIN/Ledger/prices/<cur>-cad.beancount"
   ```

   A currency pegged to one already fetched is not fetched: `[pegs]` derives it at the fixed peg. A gap in the file
   only coarsens `convert()`; it never fails the build.
6. **Export the three decision tabs** with the Sheets connector into scratch CSVs: Category
   rules (A:K), Review decisions (A:G) and Budgets (A:F). One `get_spreadsheet` call with all
   three ranges and `formattedValue` only. The connector may save a large result to the
   session's `tool-results/` folder; convert it with a script and **delete that file**.
7. **Build** with the `beancount:build` skill:

   ```bash
   KIT="$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.claude/plugins/installed_plugins.json")))["plugins"]["beancount@kattakath"][0]["installPath"])')/scripts/beancount-kit"
   "$KIT" build "$FIN/Ledger/cache" --ledger "$FIN/Ledger/ledger.toml" \
     --rules <scratch>/rules.csv --decisions <scratch>/decisions.csv \
     --accounts "$FIN/statement-extract/accounts.toml" \
     --budgets <scratch>/budgets.csv --statements "$FIN/Statements" \
     --prices "$FIN/Ledger/prices" --out "$BEANCOUNT_JOURNAL"
   ```

   - **Fava features come from their homes, never from the journal:** options and personal
     saved queries in `ledger.toml` (`[fava]`, `[[query]]`), budgets in the Budgets tab, and
     statement PDFs linked by sha256 from `Statements/`. Read `documents_missing` in the
     report: a new statement file that never extracted, or one moved out of `Statements/`.

   **The build is the reconcile.** Every statement closing and every screen figure in
   `accounts.toml` is a balance assertion; exit 3 writes nothing. Before a sync counts:
   - **add today's screen balance** to `accounts.toml` as an `[[account.balance]]`. Its
     `as_of` is the date of the **latest row the figure includes**, not the screen's "As of"
     label. Measured on TD, 2026-11-01: the screen's "As of" date was a day earlier than
     a row it counted, so `as_of` set to the label failed the reconcile;
   - **a loan read as figures, not statements** (a loan product with no export): its payments reduce the
     liability (`ledger.toml [categories]` scoped `CATEGORY@<label>`), and its `[[account]]`
     names an `interest` account. The build books what payments do not explain between two
     figures to that account. A figure is only useful **after the last payment it includes
     has synced**: two figures with no payment row between them book the principal drop as
     negative interest. Anything else bundled into the payment cannot be split from the
     interest, so name the account for both;
   - **a `[[snapshot]]` derived from a lender figure**
     is updated in `ledger.toml` in the same sync as that figure, or net worth drifts by the
     difference;
   - **always export `STATEMENT_EXTRACT_LOG`** (step 4), even for a one-off test run. Without
     it the plugin writes figures to `~/.local/state/`, outside the data folder;
   - **read the report:** `check_errors` must be 0. Check `transfer_residue` and
     `assertions_skipped_overlap` against the last sync, and explain any change;
   - **exit 3:** a balance mismatch is a missing day, a doubled file or a sign flip. Fix the
     input. Never pad over it, and never touch the journal;
   - **run `"$KIT" coverage "$FIN/Ledger/cache"` beside every build** (no gaps, no double
     counting). It must exit 0: no balance breaks, no conflicting Keys. Compare it with the
     last sync's run log: date holes, each account's coverage start, the unique Key count and
     the look-alike groups. A new hole or look-alike gets explained (boundary day? identical
     charges the bank also shows?) before the sync counts. A hole is a WARN, not a FAIL.
8. **Review** in Fava (`beancount:fava` skill, read-only, on demand): the `flag:!` entries
   and `Equity:Transfers:External`. Stop Fava when done.
   - **Group the flagged entries by merchant first:** `"$KIT" groups --out <scratch>/groups.csv`.
     Rewrite the Sheet's **Review groups** tab from it (top 50, busiest first). It is
     derived: regenerate it after every build, and never treat it as a record.
   - A group the operator gives a category becomes **one Category rule** (its `rule pattern`,
     `match_field` both). A group marked "per row" (masked counterparty) goes to Review
     decisions row by row.
   - **Pre-fill every flagged row with the `plaid-pfc:categorize` skill:** exact history →
     fuzzy → an LLM limited to the 127 names, each validated by `pfc`.
     - **Inputs:** export `"$KIT" history … --out "$FIN/Ledger/history.jsonl"`. Keep its
       working files in `$FIN/Ledger/` and delete them after.
     - **Apply the suggestions (operator policy):** the standing choice is best-fit
       automatically, not a questionnaire. Write them as Category rules over merchant
       groups, or Review decisions for one-offs, each noted
       `auto <date> (best-fit, not operator-confirmed)`. He reviews later by filtering that note.
     - **Leave transfers to a named person flagged and ask:** those categories map to specific
       accounts, so they are never guessed.
     - **Measured basis** (plaid-pfc README, 2026-11-01):
       - known merchants are about 99.5% right at ≥ 0.9;
       - fuzzy is about 83% right at ≥ 0.5;
       - the text-only LLM is 58% exact and 86% right group, so its picks always carry the
         `auto` note.
   - **Why not smart_importer:** it measured about 3 in 15 right on flagged rows. MCC, the
     global merchant code, is not in bank exports.
9. **Record each decision** in the Review decisions tab, keyed by Key, then rebuild.
   - A category in `category` wins over every rule. A decided row is never paired.
   - A payment-service link (PayPal, Remitly, Xoom) goes in `service` and `service_ref`.
     `link_sources.py` finds the links; give it `build --emit-rows` output as `--ledger`.
   - A recurring pattern belongs in **Category rules**, not in fifty decision rows.

## Categories

- **Taxonomy:** a **Plaid PFC DETAILED** value (PFCv2, published at
  `plaid.com/documents/pfc-taxonomy-all.csv`), or the literal `NEEDS_REVIEW`. The journal
  account is derived from the value; `ledger.toml [categories]` overrides it.
- **Rules:** the **Category rules** tab, their one home, since they carry names and labels. The
  build reads the tab's columns, as documented in the beancount plugin's `rules.py`.
- **Transfers between own accounts** pair one-to-one: exact amount, a Wise fee band, an FX
  band (`ledger.toml [transfers.fx]`) or an in-wallet conversion.
  - A paired leg clears through `Assets:Transfers`, which always nets to zero.
  - An unpaired leg posts to `Equity:Transfers:External` and is listed in the report.
  - A rule whose counterparty ends in `!` holds only if the row pairs; otherwise the row is
    flagged for review.
- **Unmatched rows** are flagged `!` on `Expenses:Uncategorized`. A guessed category is
  worse than a flag.

### Clearing the review queue

The procedure below clears a large queue in one session (rules plus per-row decisions)
without changing a single row that already has a category.

1. **Group first** (`"$KIT" groups`), then ask the operator by group, busiest and largest-money
   first. Bundle the obvious groups into tick-lists; ask the unclear ones one at a time.
2. **Choose the tool for each answer:**

   | Answer is about | Goes to |
   |---|---|
   | A merchant likely to recur | **A category rule** at a priority above every existing rule, so it only reaches rows nothing else matches |
   | A one-off, a masked counterparty, a closed account | **A per-row decision** |
   | A row that a must-pair rule (counterparty ending `!`) already flags | **A per-row decision**. A new rule is never reached, because the earlier rule matches first |
   | A group whose pattern is generic (`PAYPAL`, `ERROR CORRECTION`, `DEPOSIT`) | **Per-row decisions**. As a rule it would catch future rows it should not |

3. **Check every category** against Plaid's published PFC list before writing it. A name that
   looks right can be missing.
4. **Prove nothing else moved:** snapshot each Key's flag and category, rebuild, and require
   **zero** changes among rows that already had a category.
5. **Override a `TRANSFER_*` category to an expense account** (`ledger.toml [categories]`)
   **only after confirming that none of its rows is a paired transfer.** An override on a pair
   would unbalance it. Use bean-query, and count the opposite condition too.
6. **Export Review decisions with a range larger than the tab** (e.g. `A1:G2000`). A range that
   ends at the last row in use silently drops new decisions. **An export with as many rows as
   the grid means the tab is full:** compare against `gridProperties.rowCount` and add rows
   (`insert_dimension`) before writing. A new tab's default grid is small and fills
   quickly.

**Pitfall: describe a transaction by quoting its statement text, never from memory of the
merchant.** Measured 2026-11-01, three kinds of mislabel in one questionnaire, each corrected before it
was written:
- A bank code that looks like a person's name can be a re-presented debit.
- A merchant described from memory can be a different kind of business.
- A group named after a generic code can be mostly one single, named entry.

The operator answers the question as framed, so a wrong framing produces a wrong category.

## Traps

| Trap | Reality |
|---|---|
| A card export with positive purchases | OFX defines the sign from the account holder's view, so purchases are negative. If a bank breaks this, the build's balance assertions catch it. Fix the sign in the parser for that institution only |
| CSV only, no QFX | No FITID, so no stable Key. Stop and report which institution offers CSV only. Do not invent a hash key ad hoc; a fallback is its own decision |
| History limit | Portals typically offer 18–24 months. Older history comes from PDF statements, which are a separate and weaker source. State the earliest date reached |
| A pending transaction | Exports carry posted rows only. A pending charge appears once it posts, under a FITID that may be new |
| A non-spec export | ofxtools **drops a whole account** on an unknown tag and carries on. The parser makes that fatal. Fix the quirk in the parser, comment it with the bank and the date, and re-run |
| Look-alike rows | The same date, amount and payee under different FITIDs is **usually real** (TD, measured: three identical debits on one day, each with its own FITID). Check it against the screen's running balance before calling it a duplicate |

## Per institution, measured

| Institution | Export | Notes |
|---|---|---|
| **TD EasyWeb** | Accounts Overview → **Download** → "Intuit Quicken" = QFX. One file holds every account | The dialog covers the **latest statement period only**, so a top-up between statement dates also needs the account’s own activity page → Last 30 days → Download → Intuit Quicken (measured: chequing rows after the period end are only there). **Backfill per account:** for chequing and a LOC, Activity → quick filter **Last 120 days** → Download → Quicken. The Custom date range claims "up to 18 months" but rejected every date tried, three attempts. For a card, Activity → download → **one statement period at a time** (about 6 offered). The first card download routes through a legacy "Setup Download to Quicken" page that saves an account type, which is a portal setting: the operator authorizes it. Chequing and LOC FITIDs are stable across exports (re-matched across exports). Sends an empty `<ACCTTYPE>` and wraps a LOC in a mismatched `<STMTTRNRS>`; the parser repairs both. Card FITIDs embed the statement period. TD's own dialog warns that card downloads may duplicate rows |
| **CIBC Online Banking** | Per account → download → "Quicken" = QFX | Chequing and card export **full history** (from account opening). LOCs are **capped at 13 months**. **A loan product has no export**: each sync, read its detail page (balance) and add it to `accounts.toml` as an `[[account.balance]]` on that product's entry. The journal asserts it on the liability `ledger.toml` names; payments stay an expense (snapshot model). Credit terms keeps only rate, payment and terms. Exports leave out today and the 2 previous business days. Quirks the parser repairs: `CHARSET:1252` declared over a UTF-8 body; `<ACCTTYPE>` inside `CCACCTFROM`; card memos carrying `CC#<first4>****<last4>`. **Payee is mostly empty; the description sits in Memo.** A summary figure such as "Last Payment" can show a payment that was later reversed: read the transaction list, not the summary |
| **Scotiabank** | Per account → "Download as Quicken" = QFX, "All available, up to 2 years" | **Counter FITIDs:** interest, fee, cash-back and adjustment rows carry `undefined`, `undefined-1`, …, which **restart in every export**. The parser keys them by content (date, amount, payee, occurrence n), with operator approval. **`<ACCTID>` is an internal reference**, not the card or LOC number: always pass `--acct-last4 <screen last four>`, the same value on every sync, or the Keys change. Payees star-mask the counterparty but still leak 6–11 digits; the parser masks them. Older statement balances exist only as PDFs |
| **Desjardins AccèsD** | **No QFX/CSV for cards.** Statements and documents → monthly **PDF** statements → statement-extract | Content Key `Desjardins|••last4|posting date|amount|description|n` (operator-approved). The extractor emits rows **only if the statement reconciles** to its printed totals, otherwise it exits 2. The statement header prints the **account** number, not the card: always pass `--acct-last4 <card last four>`. The bulk "Download" button selected 0 statements; per-statement "View PDF" works. A saved deep link to the card page threw *SOM000026* and logged off: go in through the home-page tile. A linked **outside** account (another bank's) appears under Accounts: skip it. Accord D financing is **not** in AccèsD: read it from the statement's "Authorized Accord D financing Credit Limit" and "Accord D financing Instalment" lines (both 0 means no plan). Read any **Past Due** field the statement prints |
| **Tangerine** | Download Transactions → date range → QFX. One file per account | The date picker's own `min` attribute is the real earliest start (about 5 years). Rejected dates reveal it. The QFX labels chequing `SAVINGS`. FITIDs are account-level sequence numbers, **stable across exports** (re-matched across exports). Each card purchase also arrives with extra **$0.00 "Posted :DD Mon YYYY" rows**: the parser skips them. Real $0.00 "Interest Paid" rows are kept. The screen caps at 50 rows, so check the running balance on two windows |
| **Closed accounts (any bank)** | Monthly **PDF** statements. A bank's Accounts page usually drops a closed account, but its statement archive often **keeps listing it** for years (Scotiabank keeps statements about 7 years). Capture as in § Backfilling → statement-extract | Where the adapter has no stable ID, a synthetic Key such as `Scotiabank|••last4|statement end|line n` (**closed accounts only**: a statement never changes once issued). Direction comes from the running balance, and every row is checked. Some layouts print marketing text to the right of the balance column. A file sent from a phone may carry the **same month twice with different bytes**: count its rows once |
| **Wise** | page-lab Chromium only (the built-in pane is blocked). Statements and reports → Statements → CSV, every currency, from the date picker's earliest date → statement-extract | **Every download asks for a passkey**, which is an operator step. Statements stay available for about 30 days. Key `Wise|CUR|ID|Date Time`: Wise **reuses one ID** for a charge and its refund or reversal, and ID plus Date Time was proven stable across exports. Amounts stay in their **own currency**, with column L set. The CSV's "Payee Account Number" holds **recipients' full account numbers**: the extractor never reads it, and the files in Drive are sensitive. Rows are newest first |

## Backfilling history from the PDF archive (measured 2026-11-01)

QFX exports stop at 13 months to 2 years. Each bank's **PDF statement archive** goes back 4–6
years and closes the rest. The build owns each day (survivorship), so download whole years
and let it drop the overlap.

| Bank | Where | What worked | What did not |
|---|---|---|---|
| **TD** | Statements & Documents → account → year | The list API returns each document's `documentId`. The detail API returns the PDF as base64, but only for a document **in the list fetched most recently**, so re-list the account and year first. Save with a **real click**: inject one button and click it once per file | A scripted click on TD's own Download, or a scripted anchor click, saves nothing in the operator's Chrome. Chrome silently blocks automatic downloads until the operator allows multiple downloads for the site. LOC PDF names embed the **full account number**: rename on save |
| **CIBC** | My Documents → Account statements → account → year | Scripted clicks on CIBC's **own statement links** download `onlineStatement_<date>.pdf`. Rename per account before the next one (names collide across accounts) | Direct API calls return 403 "policy-violation": bot protection. Never work around it. No statement is issued for months with no activity |
| **Scotiabank** | Account → Statements → year | Hook `URL.createObjectURL` **before the app loads** (a page-load init script), click each "View PDF", and save the captured blob under your own name. Do a **full page load per account**: an in-app route change kept the previous account's statements | "Download all as PDF" returns a zip holding **one** statement under the placeholder name `manage.statements.pdfFilename`. Fetching the blob from the new tab fails |

- **Browser:** page-lab Chromium (the operator's choice when the built-in pane is unavailable).
  The operator signs in; sign out and close every PDF tab when done.
- **Read the page as text with numbers masked.** Screenshots show full card numbers; delete any
  saved screenshot.
- **Every refusal goes to `statement-extract:adapter-author`.** Statement PDFs have been refused
  for layout quirks such as: summary amounts on the next line, rows that
  print only their dates, a margin print number, a month split as `M ar`. Each fix shipped as
  its own PR, and the files that already worked kept identical Keys.
- **Categorise new history in bulk:** one rule per category over the merchant groups, every note
  `auto <date> (best-fit, not operator-confirmed)`, anchored patterns, priority above the last
  rule. **A transfer to a named person stays flagged**: a person-transfer category maps to
  something specific, so it is never guessed.
- **A cent no statement explains** (e.g. interest between two statements the bank never issued)
  is a `[[gap]]` in `ledger.toml` with its reason; the build asserts to the cent.

## Currency

Every amount stays in its own currency; postings never convert. `price` lines from
`Ledger/prices/` (Bank of Canada `<CUR>/CAD`, pegged currencies derived in `[pegs]`) let Fava
and `convert()` show a CAD total; they are reference rates, not what a transfer actually cost.
The Canadian banks above are `CAD`; a multi-currency wallet such as Wise holds one balance per
currency. A cross-currency transfer posts `@@` the CAD it cost, and a query adds currencies only through `convert()`.
