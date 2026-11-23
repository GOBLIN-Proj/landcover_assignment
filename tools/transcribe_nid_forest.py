"""Transcribe the forest organic-soil areas from NID 2026, Tables 6.7 (CRT 4.A.1, p.217) and 6.15 (CRT 4.A.2, p.231).

The CRT gives only the total organic forest area. The split this package needs comes from the NID:
- "Organic": drained productive N-poor organic soil;
- "Organo-mineral": drained productive N-rich soil;
- "Open area": roads, extraction routes, biodiversity areas.

The NID prints these for 1990, 1995, 2000 and 2005, and for every year from 2006 (6.7) or 2010 (6.15) to 2024.

Input is the text of the NID PDF, made with `pdftotext -layout "Ireland-NID-2026 (1).pdf" nid2026.txt`.
Each row is checked: the year must be in range and Total = Mineral + Organic to within rounding (0.15 kha).

Usage, from the repo root:
    .venv/bin/python tools/transcribe_nid_forest.py <nid2026.txt> data_sources/nid2026_forest_organic_soils.csv
"""
import re
import sys

import pandas as pd

TABLES = {
    "4.A.1": ("Table 6.7 Area (in kha) and emissions from organic soils over the time series for forest land remaining forests (CRT 4.A.1)", "NID 2026 Table 6.7 p.217"),
    "4.A.2": ("Table 6.15 Area (in kha) and emissions from different organic soils types and over the timeseries for land converted to forests (CRT 4.A.2)", "NID 2026 Table 6.15 p.231"),
}
COLUMNS = ["total_area_kha", "mineral_kha", "organic_kha", "open_area_kha", "drained_n_poor_organic_kha",
           "drained_n_rich_organo_mineral_kha"]
# Rows where the NID's own figures don't add up. Each is kept as printed, with a note.
KNOWN_INCONSISTENCIES = {
    ("4.A.2", 2024): "NID prints total 266.0 = mineral 140.1 + organic 126.3 (= 266.4). CRT 2026 4.A.2 (2024) has "
                     "265.961 / 140.083 / 125.877, so the NID organic value is 0.4 kha above the CRT.",
}
ROW = re.compile(r"^\s{2,}(19\d\d|20\d\d)\s+" + r"\s+".join([r"(-?\d+\.\d)"] * 6))


def transcribe(text_path):
    lines = open(text_path, encoding="utf-8").read().splitlines()
    out = []
    for category, (title, source) in TABLES.items():
        start = [i for i, line in enumerate(lines) if line.strip() == title]
        if len(start) != 1:
            raise ValueError(f"{category}: table title found {len(start)} times")
        rows = []
        for line in lines[start[0] + 1:start[0] + 60]:
            if line.strip().startswith("1 Total area includes"):
                break
            m = ROW.match(line)
            if m:
                year, *vals = m.groups()
                rows.append(dict(category=category, year=int(year), **dict(zip(COLUMNS, map(float, vals))),
                                 source=source, note=KNOWN_INCONSISTENCIES.get((category, int(year)), "")))
        if not rows or rows[-1]["year"] != 2024:
            raise ValueError(f"{category}: table did not end in 2024")
        for r in rows:
            if abs(r["total_area_kha"] - r["mineral_kha"] - r["organic_kha"]) > 0.15 and not r["note"]:
                raise ValueError(f"{category} {r['year']}: total != mineral + organic")
        out += rows
    return pd.DataFrame(out)


if __name__ == "__main__":
    df = transcribe(sys.argv[1])
    df.to_csv(sys.argv[2], index=False, lineterminator="\n")
    print(f"{sys.argv[2]}: {len(df)} rows ({df.groupby('category').year.agg(['min', 'max', 'count']).to_dict('index')})")
