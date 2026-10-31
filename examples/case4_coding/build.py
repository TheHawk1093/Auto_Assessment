"""Builds the Case 4 materials: a coding-and-report assignment and seven students' zips.

Run `python examples/case4_coding/build.py` to rewrite `submissions/<roll>.zip` from the sources
below. Everything here is invented for the demo; the code is deliberately wrong in places.

What each student is designed to show (the marks are out of 6, 6, 8 and 10):

| Student | Code | Report |
|---|---|---|
| S24001 (A) | all three functions correct | complete derivation, roots, discriminant (Word, with equations) |
| S24002 (B) | all correct | derivation and roots, no discriminant explanation |
| S24003 (C) | q1 ignores punctuation, q2 off by one, q3 correct | derivation skips the key step |
| S24004 (D) | q2 syntax error, q3 left unfinished | complete (Word, with equations) |
| S24005 (E) | q2 never ends (endless loop), q3 wrong exception | complete |
| S24006 (F) | q2 and q3 missing | complete |
| S24007 (G) | one file `solution.py` with everything, correct; files not named by question | complete |
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

HERE = Path(__file__).parent

Q1_OK = """def is_palindrome(s):
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]
"""
Q1_BUG = """def is_palindrome(s):
    # compares the raw text, so spaces and punctuation break it
    return s.lower() == s.lower()[::-1]
"""
Q2_OK = """def fizzbuzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
"""
Q2_OFF = """def fizzbuzz(n):
    out = []
    for i in range(1, n):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
"""
Q2_SYNTAX = """def fizzbuzz(n)
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0
            out.append("Fizz")
        else:
            out.append(str(i))
    return out
"""
Q2_LOOP = """def fizzbuzz(n):
    out = []
    i = 1
    while i <= n:
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
        # forgot to add 1 to i
    return out
"""
Q3_OK = """import math


def mean_std(values):
    if not values:
        raise ValueError("no values")
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, math.sqrt(var)
"""
Q3_TODO = """def mean_std(values):
    # TODO: work out the mean first, then the spread
    pass
"""
Q3_WRONG_ERROR = """import math


def mean_std(values):
    mean = sum(values) / len(values)  # ZeroDivisionError for an empty list
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, math.sqrt(var)
"""

REPORT_FULL = """# Quadratic formula

**Derivation.** Start from a x^2 + b x + c = 0 with a not equal to 0. Divide by a:

\\[ x^2 + \\frac{b}{a} x + \\frac{c}{a} = 0 \\]

Move the constant and complete the square by adding \\( (b/2a)^2 \\) to both sides:

\\[ x^2 + \\frac{b}{a} x + \\frac{b^2}{4a^2} = \\frac{b^2}{4a^2} - \\frac{c}{a} \\]

\\[ \\left(x + \\frac{b}{2a}\\right)^2 = \\frac{b^2 - 4ac}{4a^2} \\]

Taking square roots gives

\\[ x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a} \\]

**Example.** For x^2 - 5x + 6 = 0, a = 1, b = -5, c = 6, so b^2 - 4ac = 25 - 24 = 1 and
x = (5 +- 1)/2, giving x = 3 or x = 2. Check: 3^2 - 15 + 6 = 0 and 2^2 - 10 + 6 = 0.

**Discriminant.** D = b^2 - 4ac. If D > 0 there are two distinct real roots, if D = 0 one repeated
real root, and if D < 0 there are no real roots (two complex ones). Here D = 1 > 0.
"""
REPORT_NO_DISC = REPORT_FULL.split("**Discriminant.**")[0].rstrip() + "\n"
REPORT_SKIPS = """# Quadratic formula

**Derivation.** Start from a x^2 + b x + c = 0. Divide by a, then complete the square and we get
the formula

\\[ x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a} \\]

**Example.** For x^2 - 5x + 6 = 0 the roots are 2 and 3 because 2 times 3 is 6 and 2 plus 3 is 5.

**Discriminant.** It is the part under the root. If it is negative there is no real answer.
"""


def docx(markdown: str) -> bytes:
    """A minimal valid Word file: ordinary text as runs, equations as Word math (OMML)."""
    from xml.sax.saxutils import escape

    paragraphs = []
    for line in markdown.splitlines():
        line = line.strip().lstrip("# ").replace("**", "")
        if not line:
            continue
        if line.startswith("\\[") and line.endswith("\\]"):
            math = line[2:-2].strip()
            paragraphs.append(
                f"<w:p><m:oMathPara><m:oMath><m:r><m:t>{escape(math)}</m:t></m:r></m:oMath>"
                "</m:oMathPara></w:p>"
            )
        else:
            paragraphs.append(
                f'<w:p><w:r><w:t xml:space="preserve">{escape(line)}</w:t></w:r></w:p>'
            )
    body = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><w:body>'
        + "".join(paragraphs)
        + "</w:body></w:document>"
    )
    types = (
        '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/'
        'package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.'
        'openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="'
        'application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.'
        'openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://'
        'schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", body)
    return buf.getvalue()


# roll number -> {file name: text or bytes}
STUDENTS: dict[str, dict[str, str | bytes]] = {
    "S24001": {"q1.py": Q1_OK, "q2.py": Q2_OK, "q3.py": Q3_OK, "q4_report.docx": docx(REPORT_FULL)},
    "S24002": {"q1.py": Q1_OK, "q2.py": Q2_OK, "q3.py": Q3_OK, "q4_report.md": REPORT_NO_DISC},
    "S24003": {"q1.py": Q1_BUG, "q2.py": Q2_OFF, "q3.py": Q3_OK, "q4_report.md": REPORT_SKIPS},
    "S24004": {
        "q1.py": Q1_OK,
        "q2.py": Q2_SYNTAX,
        "q3.py": Q3_TODO,
        "q4_report.docx": docx(REPORT_FULL),
    },
    "S24005": {
        "q1.py": Q1_OK,
        "q2.py": Q2_LOOP,
        "q3.py": Q3_WRONG_ERROR,
        "q4_report.md": REPORT_FULL,
    },
    "S24006": {"q1.py": Q1_OK, "q4_report.md": REPORT_FULL},
    "S24007": {"solution.py": "\n\n".join([Q1_OK, Q2_OK, Q3_OK]), "report.md": REPORT_FULL},
}


def build() -> None:
    """Write one zip per student into submissions/, and the folders they were built from."""
    out = HERE / "submissions"
    out.mkdir(exist_ok=True)
    for roll, files in STUDENTS.items():
        with zipfile.ZipFile(out / f"{roll}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for name, content in files.items():
                z.writestr(name, content)
    print(f"wrote {len(STUDENTS)} zips to {out}")


if __name__ == "__main__":
    build()
