#!/usr/bin/env python3
"""Build a compact ZIP -> lat/lon lookup bundled with the app.

Source: U.S. Census ZCTA Gazetteer (public domain). Produces a fixed-width,
zip-sorted file (data/zips.dat) so BrightScript can binary-search it quickly
with no geocoding API call.

Record layout (fixed width, no delimiters), width = 24 bytes:
    zip  : 5 chars (5-digit ZCTA, zero-padded)
    lat  : 9 chars, left-justified, space-padded (e.g. "41.7506  ")
    lon  : 10 chars, left-justified, space-padded (e.g. "-88.2017  ")
Records are concatenated with no newline; record count = filesize / 24.
"""
import os
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TMP = os.path.join(ROOT, "tmp")
SRC_URL = ("https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
           "2023_Gazetteer/2023_Gaz_zcta_national.zip")
TXT = os.path.join(TMP, "2023_Gaz_zcta_national.txt")

REC_W = 24
ZIP_W, LAT_W, LON_W = 5, 9, 10


def ensure_source():
    os.makedirs(TMP, exist_ok=True)
    if os.path.exists(TXT):
        return
    zpath = os.path.join(TMP, "zcta.zip")
    print("downloading Census ZCTA gazetteer...")
    urllib.request.urlretrieve(SRC_URL, zpath)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(TMP)


def build():
    ensure_source()
    rows = []
    with open(TXT, encoding="latin-1") as f:
        header = f.readline()  # skip header
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 7:
                continue
            zc = parts[0].strip()
            lat = parts[5].strip()
            lon = parts[6].strip()
            if len(zc) != 5 or not zc.isdigit():
                continue
            try:
                latf = float(lat)
                lonf = float(lon)
            except ValueError:
                continue
            rows.append((int(zc), zc, f"{latf:.4f}", f"{lonf:.4f}"))

    rows.sort(key=lambda r: r[0])
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "zips.dat")
    with open(out, "w", encoding="ascii") as f:
        for _, zc, lat, lon in rows:
            rec = zc[:ZIP_W].ljust(ZIP_W) + lat.ljust(LAT_W) + lon.ljust(LON_W)
            assert len(rec) == REC_W, (rec, len(rec))
            f.write(rec)

    print(f"wrote {len(rows)} zip records -> {out} ({len(rows) * REC_W} bytes)")


if __name__ == "__main__":
    build()
