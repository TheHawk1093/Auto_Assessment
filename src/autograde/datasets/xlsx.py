"""A minimal .xlsx reader (first worksheet, cell values as text).

It means no spreadsheet library is needed to load the datasets that ship as Excel files.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def _column(ref: str) -> int:
    """Zero-based column number of a cell reference such as AB12."""
    letters = re.match(r"[A-Z]+", ref).group()
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path: Path, sheet: int = 1) -> list[list[str]]:
    """Rows of the sheet as lists of strings; empty cells are empty strings."""
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        sheet_xml = ET.fromstring(z.read(f"xl/worksheets/sheet{sheet}.xml"))
    rows: list[list[str]] = []
    for row in sheet_xml.iter(f"{{{NS['m']}}}row"):
        cells: dict[int, str] = {}
        for c in row.findall("m:c", NS):
            v = c.find("m:v", NS)
            if c.get("t") == "inlineStr":
                text = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
            elif v is None or v.text is None:
                text = ""
            elif c.get("t") == "s":
                text = shared[int(v.text)]
            else:
                text = v.text
            cells[_column(c.get("r"))] = text
        width = max(cells) + 1 if cells else 0
        rows.append([cells.get(i, "") for i in range(width)])
    return rows
