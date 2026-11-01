---
name: verify-package-document
description: Verify a PDF before it counts as held — page count, real text vs scan, SIN exposure, leftover placeholders — then name and file it. Use after any download, before adding a document to a package, and before telling the operator a document is in hand.
argument-hint: "[file path]"
---

# Verify a document before it counts

**A filename is not evidence. A file size is not evidence.** Run the checks.

```bash
F="path/to.pdf"
pdfinfo "$F" | awk '/^Pages:/{print $2}'                      # pages
pdftotext "$F" - | wc -c                                      # total characters
pdftotext "$F" - | grep -oE '[0-9X]{3}[ -][0-9X]{3}[ -][0-9X]{3}' | sort -u   # SIN-shaped
pdftotext "$F" - | grep -oE '\[[A-Z /]+\]' | sort -u          # placeholders
pdfimages -list "$F"                                          # true scan resolution
```

## Reading the output

| Signal | Means |
|---|---|
| **~50–60 chars/page** | an **image scan**, not text. Fine for ID, useless for anything a reader must search |
| **500+ chars/page** | real text |
| **0 characters** | a pure image. Expected for a passport or licence scan; alarming for a statement |
| A SIN-shaped match | **check it** — phone fragments like `800-959-828` match the same pattern. Only `XXX XX1 234`-style or a real nine-digit group counts |
| Any `[BRACKETED]` string | a draft escaped into a signable document. **Fix before anyone sees it** |
| `pdfimages` x-ppi | 300 ppi is a good scan; 150 ppi is a downsample. **A newer file is not automatically better** |

## The placeholder check is not optional

A letter went out once carrying `[FIRM NAME]`. The grep above takes a second. Where a
bracket can never be filled — a firm address nobody has, a file number that does not exist —
**delete the line**, do not leave the bracket.

## Naming

`NN-topic-detail[-YYYY-MM-DD].pdf`, numbered by its place on the request list, so the folder
sorts into the order it will be sent. Variants take a letter: `09-`, `09b-`.

## Then

Record **pages and bytes** in the inventory table of the matter's package Doc, and whether it carries an
identifier in full. Record nothing about status there — that goes to the Tasks list. A document is "held" only once it has been through this.
