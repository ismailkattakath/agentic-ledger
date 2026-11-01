# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Link payment-service records (the "Source details" tab) to the ledger rows that funded them.

Procedure only. Service names, payee patterns, merchants and amounts arrive as inputs; this
file holds none of them.

Inputs
  --sources  JSON list of source records. Fields used:
               source   service label (matched against --payee)
               id       the service's own transaction/reference id
               date     ISO date the service shows for the record
               charge   amount the funding account was charged, positive, in `currency`
                        (amount sent + fee, or the gross purchase)
               alt      optional list of other plausible charges (e.g. amount without the fee)
               currency ISO code of `charge`
  --ledger   JSON list of ledger rows, either `beancount-kit build --emit-rows` output
             (columns A-L) or the legacy [sheet_row, date, amount, payee, memo, institution,
             account, category, key, currency] (amount negative = money out)
  Each link becomes a "Review decisions" row: key, service = source, service_ref = id.
  --payee    SOURCE=REGEX, repeatable. A ledger row is a candidate for SOURCE only if
             "<payee> <memo>" matches REGEX (case-insensitive)
  --window   ledger date minus source date, in days, inclusive (default -2:5)
  --tol      absolute amount tolerance (default 0.01)

Matching
  Candidates: ledger outflow, same currency, payee matches, date inside the window, and
  |ledger amount| equal to `charge` (exact) or to one of `alt` (alt) within --tol.
  Score = (alt?, |day gap|). Greedy one-to-one by ascending score. A source record whose
  best remaining score is shared by two ledger rows, or a ledger row whose best remaining
  score is shared by two source records, is AMBIGUOUS: left unlinked, never guessed.

Output (stdout or --out): JSON list, one per source record:
  {source, id, key, row, method, confidence}
  method      "charge+date+payee" | "alt-charge+date+payee" | ""
  confidence  "high" (exact charge, |gap| <= 2) | "medium" | "ambiguous" | "no match"
Summary per source on stderr.

    uv run --script link_sources.py --sources src.json --ledger ledger.json \\
        --payee <SOURCE>=<REGEX> --out links.json
"""

import argparse
import collections
import datetime as dt
import json
import re
import sys


def day(s):
    return dt.date.fromisoformat(str(s)[:10])


def money(v):
    return float(str(v).replace(",", "").replace("$", "") or 0)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--sources", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--payee", action="append", default=[], help="SOURCE=REGEX")
    ap.add_argument("--window", default="-2:5")
    ap.add_argument("--tol", type=float, default=0.01)
    ap.add_argument("--out")
    a = ap.parse_args()

    lo, hi = (int(v) for v in a.window.split(":"))
    pats = {}
    for p in a.payee:
        k, _, rx = p.partition("=")
        pats[k] = re.compile(rx, re.I)

    sources = json.load(open(a.sources, encoding="utf-8"))
    ledger = []
    for i, r in enumerate(json.load(open(a.ledger, encoding="utf-8"))):
        if len(r) == 12:  # beancount-kit build --emit-rows: columns A-L, no row number
            ledger.append(
                dict(
                    row=i,
                    date=day(r[0]),
                    amt=money(r[1]),
                    text=f"{r[2]} {r[3]}",
                    key=r[8],
                    cur=r[11] or "CAD",
                )
            )
            continue
        r = list(r) + [""] * (10 - len(r))
        ledger.append(
            dict(
                row=int(r[0]),
                date=day(r[1]),
                amt=money(r[2]),
                text=f"{r[3]} {r[4]}",
                key=r[8],
                cur=r[9] or "CAD",
            )
        )

    cands = []
    for si, s in enumerate(sources):
        rx = pats.get(s["source"])
        if rx is None:
            continue
        sd = day(s["date"])
        charges = [(0, float(s["charge"]))] + [
            (1, float(x)) for x in s.get("alt") or []
        ]
        for li, l in enumerate(ledger):
            if (
                l["amt"] >= 0
                or l["cur"] != s.get("currency", "CAD")
                or not rx.search(l["text"])
            ):
                continue
            dd = (l["date"] - sd).days
            if not lo <= dd <= hi:
                continue
            for is_alt, c in charges:
                if abs(-l["amt"] - c) <= a.tol:
                    cands.append(((is_alt, abs(dd)), si, li))
                    break
    cands.sort()

    s_link, l_used, ambiguous = {}, set(), set()
    remaining = cands
    while remaining:
        score, si, li = remaining[0]
        if si in s_link or li in l_used or si in ambiguous:
            remaining = remaining[1:]
            continue
        live = [
            c
            for c in remaining
            if c[1] not in s_link and c[1] not in ambiguous and c[2] not in l_used
        ]
        same_s = {c[2] for c in live if c[1] == si and c[0] == score}
        same_l = {c[1] for c in live if c[2] == li and c[0] == score}
        if len(same_s) > 1:
            ambiguous.add(si)
        elif len(same_l) > 1:
            ambiguous.update(same_l)
        else:
            s_link[si] = (li, score)
            l_used.add(li)
        remaining = [
            c
            for c in remaining[1:]
            if c[1] not in s_link and c[1] not in ambiguous and c[2] not in l_used
        ]

    out, summary = [], collections.defaultdict(collections.Counter)
    for si, s in enumerate(sources):
        rec = dict(
            source=s["source"],
            id=s["id"],
            key="",
            row="",
            method="",
            confidence="no match",
        )
        if si in s_link:
            li, (is_alt, gap) = s_link[si]
            rec.update(
                key=ledger[li]["key"],
                row=ledger[li]["row"],
                method="alt-charge+date+payee" if is_alt else "charge+date+payee",
                confidence="high" if not is_alt and gap <= 2 else "medium",
            )
        elif si in ambiguous:
            rec["confidence"] = "ambiguous"
        out.append(rec)
        summary[s["source"]][rec["confidence"]] += 1

    keys = [r["key"] for r in out if r["key"]]
    if len(keys) != len(set(keys)):
        sys.exit("internal error: a ledger key was linked twice")
    text = json.dumps(out, indent=0)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
    else:
        print(text)
    for src, c in sorted(summary.items()):
        print(
            f"{src}: {sum(c.values())} records  "
            + "  ".join(f"{k} {v}" for k, v in sorted(c.items())),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
