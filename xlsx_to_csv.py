#!/usr/bin/env python3
"""Convert the Brady/Giglio xlsx into the cleaned CSV that the dashboard
(illinois-brady-giglio-embed.html) loads.

Columns are the dashboard's record keys:
    n, id, role, cty, dept, d, dk, cat, src, st, ag, cc
(d = display date, dk = sortable YYYYMMDD; YYYY0000 for year-only, 0 if blank)

Usage:
    python xlsx_to_csv.py Brady_Giglio_Statewide_List_for_Pulitzer.xlsx
    python xlsx_to_csv.py in.xlsx --out brady_giglio_cleaned.csv
"""
import argparse
import csv
import datetime as dt
import re
import sys

import openpyxl

# AP-style month abbreviations
AP_MONTHS = ["Jan.", "Feb.", "March", "April", "May", "June",
             "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
EXCEL_EPOCH = dt.datetime(1899, 12, 30)
YEAR_ONLY_CUTOFF = 1950  # real findings are all later than this

STATUS_FIXES = {"No lllinois LE Employment": "No Illinois law enforcement employment"}


def text(v):
    """Cell -> stripped string ('' for blank)."""
    return "" if v is None else str(v).strip()


def parse_date(v):
    """Return (display string, sortable YYYYMMDD int; YYYY0000 for year-only; 0 if blank)."""
    if v is None or (isinstance(v, str) and not v.strip()):
        return "", 0
    if isinstance(v, dt.datetime):
        if v.year < YEAR_ONLY_CUTOFF:
            # Year typed as a number (e.g. 2018) but cell formatted as a date,
            # so it loads as a 1905 date; the serial number is the year.
            year = (v - EXCEL_EPOCH).days
            return str(year), year * 10000
        return f"{AP_MONTHS[v.month - 1]} {v.day}, {v.year}", v.year * 10000 + v.month * 100 + v.day
    s = str(v).strip()
    m = re.search(r"\b(1[89]\d\d|20\d\d)\b", s)
    return s, int(m.group(1)) * 10000 if m else 0


def clean_row(row):
    name, id_, cty, dept, date, cat, src, st, ag, cc = (list(row) + [None] * 10)[:10]
    # Some rows have a job title typed in the ID column.
    role, id_str = "", ""
    if isinstance(id_, str):
        role = id_.strip()
    elif id_ is not None:
        id_str = str(int(id_)) if isinstance(id_, (int, float)) else str(id_).strip()
    d, dk = parse_date(date)
    st = text(st)
    ag = text(ag)
    return {
        "n": text(name), "id": id_str, "role": role, "cty": text(cty),
        "dept": text(dept), "d": d, "dk": dk, "cat": text(cat), "src": text(src),
        "st": STATUS_FIXES.get(st, st),
        "ag": "" if ag == "None" else ag,
        "cc": text(cc),
    }


def convert(xlsx_path):
    ws = openpyxl.load_workbook(xlsx_path, data_only=True).active
    rows = ws.iter_rows(min_row=2, values_only=True)  # row 1 = headers
    return [clean_row(r) for r in rows if any(c is not None and str(c).strip() for c in r)]


FIELDS = ["n", "id", "role", "cty", "dept", "d", "dk", "cat", "src", "st", "ag", "cc"]


def write_csv(records, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(records)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx")
    ap.add_argument("--out", default="brady_giglio_cleaned.csv", help="output CSV path")
    a = ap.parse_args()

    records = convert(a.xlsx)
    write_csv(records, a.out)
    print(f"Wrote {a.out}", file=sys.stderr)
    print(f"{len(records)} records | year-only dates: {sum(1 for r in records if r['dk'] % 10000 == 0 and r['dk'])}"
          f" | blank dates: {sum(1 for r in records if not r['dk'])}"
          f" | role rows: {sum(1 for r in records if r['role'])}", file=sys.stderr)


if __name__ == "__main__":
    main()
