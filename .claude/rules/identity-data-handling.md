# Identity and account data — what may be written, and where

## Never written anywhere

A **SIN**, a **full bank account number**, a **full card number**, a **NETFILE access code**,
a **CRA security code**, a password or an OTP. Not in a reply, not in a file, not in a commit,
not in a task note.

If the operator pastes one, it does not get echoed back. If a document contains one, that
fact is reported — *"this PDF carries the full SIN"* — and the number is not.

## Written as last four only

Account and card identifiers. Format: `••1234`.

## Clipboard, not screen

Anything the operator must paste — an access code, a one-time code, a long reference — goes
to the clipboard (`pbcopy`) and is named, never displayed.

## Which copy of a document to prefer

When two versions of the same document exist, prefer the one that **masks** the identifier,
even at lower quality, and say which is which. Never assume a document type masks: two
documents from the same issuer can differ, so check each file. A masked SIN reads like
`XXX XX1 234`; a full one is three groups of three digits.

The check is one command, and it is not optional before a document is called safe:

```bash
pdftotext F.pdf - | grep -oE '[0-9X]{3}[ -][0-9X]{3}[ -][0-9X]{3}' | sort -u
```

Phone-number fragments match that pattern too — read the output, do not just count it.

## This repository

Holds procedures only. No balances, no account numbers, no document files. The data folder
is named in CLAUDE.md; its contents stay there.
