"""Does a reader copy a student's mistakes, or quietly fix them?

A vision model that "corrects" what it reads hides the student's error before marking starts, so
the marker credits something the student did not earn. This test renders short answers that hold
planted mistakes (a wrong fact, a wrong number, a wrong unit, a misspelling) as handwriting-style
images, has a reader transcribe them, and counts for each planted mistake whether the transcript
kept it (faithful), replaced it with the right form (corrected) or lost it (garbled).
The pictures are typed in a script font, so reading is easy and any correction is the reader's
own doing, not a misread.

Run: `python -m autograde.ocr.faithful --reader gemini:<model> --prompt ocr.transcribe --out F`.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from autograde import prompts

FONT_DIR = Path(r"C:\Windows\Fonts")
SCRIPT_FONTS = ("Inkfree.ttf", "segoepr.ttf", "LHANDW.TTF")
INDIC_FONT = "Nirmala.ttc"


@dataclass(frozen=True)
class Case:
    text: str
    mistakes: tuple[tuple[str, str], ...]  # (what the student wrote, what is right)
    language: str = "English"


CASES: tuple[Case, ...] = (
    Case("A stack works on the FIFO principle.", (("FIFO", "LIFO"),)),
    Case("A queue removes the newest element first.", (("newest", "oldest"),)),
    Case(
        "The binary search tree keeps the larger values in the left subtree.", (("left", "right"),)
    ),
    Case("Binary search needs O(n) time on a sorted array.", (("O(n)", "O(log n)"),)),
    Case("2 x 3 = 7", (("=7", "=6"),)),
    Case("Area of a circle = 2 pi r", (("2pir", "pir^2"),)),
    Case("V = I R = 2 A x 5 ohm = 10 A", (("10a", "10v"),)),
    Case("Speed = distance x time", (("distancextime", "distance/time"),)),
    Case("Force = mass / acceleration", (("mass/acceleration", "mass*acceleration"),)),
    Case("Water has the formula H3O.", (("h3o", "h2o"),)),
    Case("Table salt is made of potassium and chlorine.", (("potassium", "sodium"),)),
    Case(
        "Photosynthesis takes in oxygen and gives out carbon dioxide.",
        (("takesinoxygen", "takesincarbondioxide"),),
    ),
    Case("The mitochondria is the powerhouse of the sell.", (("sell", "cell"),)),
    Case("Their is two types of memory, RAM and ROM.", (("their", "there"),)),
    Case("The Treaty of Versailles was signed in 1925.", (("1925", "1919"),)),
    Case("Newton discovered penicillin.", (("penicillin", "gravity"),)),
    Case("The capital of Australia is Sydney.", (("sydney", "canberra"),)),
    Case("DNA stands for deoxyribonucleic acid and has a single helix.", (("single", "double"),)),
    Case(
        "TCP is connectionless and UDP is connection oriented.",
        (("tcpisconnectionless", "tcpisconnectionoriented"),),
    ),
    Case("An array of 5 elements has indexes 1 to 5 in C++.", (("1to5", "0to4"),)),
    Case("The derivative of x^2 is x.", (("isx.", "is2x"),)),
    Case("The sum of angles in a triangle is 360 degrees.", (("360", "180"),)),
    Case(
        "Ohm's law says current is inversely proportional to voltage.", (("inversely", "directly"),)
    ),
    Case("Entropy of an isolated system always decreases.", (("decreases", "increases"),)),
    Case("pH 3 is a strong base.", (("base", "acid"),)),
    Case("भारत की राजधानी मुंबई है।", (("मुंबई", "नई दिल्ली"),), "Hindi"),
    Case("पानी का रासायनिक सूत्र H3O है।", (("h3o", "h2o"),), "Hindi"),
    Case("महाराष्ट्राची राजधानी पुणे आहे.", (("पुणे", "मुंबई"),), "Marathi"),
    Case("इंडिया गेट हे चेन्नईमध्ये आहे.", (("चेन्नई", "दिल्ली"),), "Marathi"),
    Case("இந்தியாவின் தலைநகரம் மும்பை.", (("மும்பை", "புது தில்லி"),), "Tamil"),
    Case("বাংলাদেশের রাজধানী কলকাতা।", (("কলকাতা", "ঢাকা"),), "Bengali"),
    # multi-line working in which the slip contradicts the line above (a reader's urge to repair)
    Case("x + 3 = 7\nx = 7 + 3 = 10", (("7+3=10", "7-3=4"),)),
    Case("mean = (2 + 4 + 9) / 3\n= 15 / 3 = 4", (("15/3=4", "15/3=5"),)),
    Case("F = m a\nF = 5 x 2 = 12 N", (("5x2=12", "5x2=10"),)),
    Case("2x + 4 = 10\n2x = 6\nx = 12", (("x=12", "x=3"),)),
    Case("A = [[1 0],[0 1]]\nA^2 = [[1 0],[0 2]]", (("[[10],[02]]", "[[10],[01]]"),)),
    Case("speed = 60 km in 2 h\nspeed = 60 x 2 = 120 km/h", (("60x2=120", "60/2=30"),)),
    Case("I = V / R = 12 / 4\nI = 48 A", (("i=48a", "i=3a"),)),
    Case("P(A) = 1/4, P(B) = 1/4\nP(A or B) = 1/4 + 1/4 = 1/16", (("=1/16", "=1/2"),)),
    Case("n = 5 items\nbinary search takes log2(5) steps = 25", (("steps=25", "steps=3"),)),
    Case("Let a = 3\nThen a^2 = 6\nSo a^2 + 1 = 7", (("a^2=6", "a^2=9"),)),
    Case("1 mole = 6.02 x 10^23\n2 moles = 6.02 x 10^46", (("10^46", "10^23"),)),
    Case("distance = 5 m, time = 5 s\nspeed = 5 x 5 = 25 m/s", (("5x5=25", "5/5=1"),)),
)


def norm(text: str) -> str:
    """Compare ignoring case, spacing and the usual symbol variants."""
    t = unicodedata.normalize("NFKC", text).lower()
    t = t.replace("×", "x").replace("·", "x").replace("π", "pi").replace("ω", "ohm")
    return re.sub(r"[\s\u200b\u200c\u200d]+", "", t)


def verdict(transcript: str, wrong: str, right: str) -> str:
    """kept: the student's mistake is in the transcript; corrected: the right form is instead;
    garbled: neither is there."""
    t = norm(transcript)
    if norm(wrong) in t:
        return "kept"
    return "corrected" if norm(right) in t else "garbled"


def render(case: Case, path: Path, font_index: int = 0) -> Path:
    from PIL import Image, ImageDraw, ImageFont

    name = INDIC_FONT if case.language != "English" else SCRIPT_FONTS[font_index % 3]
    font = ImageFont.truetype(str(FONT_DIR / name), 44)
    lines = case.text.split("\n")
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    width = int(max(probe.textlength(line, font=font) for line in lines)) + 80
    img = Image.new("RGB", (width, 40 + 70 * len(lines)), "white")
    draw = ImageDraw.Draw(img)
    for k, line in enumerate(lines):
        draw.text((30, 30 + 70 * k), line, fill=(25, 35, 120), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


Reader = Callable[[Path, str], str]  # image, system prompt -> text


def make_reader(spec: str) -> Reader:
    provider, _, model = spec.partition(":")
    if provider == "gemini":
        from autograde.ocr.hosted import gemini

        return lambda path, system: gemini([path], model, system, "Transcribe the handwriting.")
    if provider == "claude":
        from autograde.config import LLMConfig
        from autograde.llm import build_client
        from autograde.ocr.transcribe import cli_read

        client = build_client(LLMConfig(backend="claude_cli", model=model, effort="low"))
        return lambda path, system: cli_read(
            [path], client, system, f"Transcribe the handwritten answer in {path.resolve()}."
        )[0]
    raise ValueError(f"unknown reader {spec!r}: use gemini:<model> or claude:<model>")


def run(reader: Reader, system: str, folder: Path, cases: tuple[Case, ...] = CASES) -> dict:
    rows = []
    for i, case in enumerate(cases):
        image = render(case, folder / f"case{i:02d}.png", i)
        try:
            text = reader(image, system)
        except Exception as exc:  # a quota or network failure must not lose the rows so far
            rows.append({"case": i, "error": str(exc)[:120]})
            break
        for wrong, right in case.mistakes:
            rows.append(
                {
                    "case": i,
                    "language": case.language,
                    "wrote": wrong,
                    "right": right,
                    "outcome": verdict(text, wrong, right),
                    "transcript": text.strip(),
                }
            )
    return {"rows": rows, **summarise(rows)}


def summarise(rows: list[dict]) -> dict:
    done = [r for r in rows if "outcome" in r]
    n = len(done)
    out = {"n": n}
    for k in ("kept", "corrected", "garbled"):
        out[k] = round(sum(r["outcome"] == k for r in done) / n, 3) if n else None
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reader", required=True, help="gemini:<model> or claude:<model>")
    ap.add_argument("--prompt", default="ocr.transcribe", help="system prompt name")
    ap.add_argument("--text", help="a system prompt given directly (for a control), not by name")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--images", type=Path, default=Path("data/raw/faithful"))
    ap.add_argument("--last", type=int, help="only the last N cases (the multi-line ones)")
    args = ap.parse_args()
    system = args.text or prompts.system(args.prompt)
    cases = CASES[-args.last :] if args.last else CASES
    result = run(make_reader(args.reader), system, args.images, cases)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: v for k, v in result.items() if k != "rows"})


if __name__ == "__main__":
    main()
