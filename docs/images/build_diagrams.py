"""Draw the documentation diagrams as SVG files (vector, so they stay sharp at any size).

Run from the repository root:  python docs/images/build_diagrams.py
Writes workflow.svg, app-flow.svg, architecture.svg, answer-trace.svg and ocr-fallback.svg here.
Each diagram sits on its own white card, so it reads the same on light and dark pages, and ends
with a colour legend.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).parent
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
INK, MUTED, LINE = "#1f2937", "#6b7280", "#9ca3af"
TONES = {  # name -> (fill, stroke)
    "blue": ("#dbeafe", "#2563eb"),
    "green": ("#d1fae5", "#059669"),
    "amber": ("#fef3c7", "#d97706"),
    "purple": ("#ede9fe", "#7c3aed"),
    "red": ("#fee2e2", "#dc2626"),
    "grey": ("#f3f4f6", "#6b7280"),
}


class Svg:
    """A tiny SVG builder: boxes, arrows, text and a legend on a white card."""

    def __init__(self, w: int, h: int, title: str, subtitle: str = "") -> None:
        self.w, self.h = w, h
        self.parts: list[str] = []
        self.text(32, 44, title, size=24, weight=700)
        if subtitle:
            self.text(32, 70, subtitle, size=15, fill=MUTED)

    def text(self, x, y, s, size=14, weight=400, fill=INK, anchor="start") -> None:
        self.parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{escape(s)}</text>'
        )

    def box(self, x, y, w, h, title, lines=(), tone="blue", radius=12, tsize=16) -> None:
        fill, stroke = TONES[tone]
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.6"/>'
        )
        n = len(lines)
        top = y + h / 2 - (n * 9) - (4 if n else -5)
        self.text(x + w / 2, top, title, size=tsize, weight=700, anchor="middle")
        for i, line in enumerate(lines):
            self.text(x + w / 2, top + 22 + i * 18, line, size=13, fill=MUTED, anchor="middle")

    def group(self, x, y, w, h, label, tone="grey", right=False) -> None:
        _, stroke = TONES[tone]
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="none" '
            f'stroke="{stroke}" stroke-width="1.4" stroke-dasharray="7 6"/>'
        )
        if right:  # label in the top right corner, clear of arrows entering from the left
            self.text(x + w - 16, y + 24, label, size=13, weight=700, fill=stroke, anchor="end")
        else:
            self.text(x + 16, y + 24, label, size=13, weight=700, fill=stroke)

    def arrow(self, x1, y1, x2, y2, label="", dash=False, color=LINE, lx=None, ly=None) -> None:
        d = ' stroke-dasharray="6 5"' if dash else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{d} '
            f'marker-end="url(#head)"/>'
        )
        if label:
            mx = lx if lx is not None else (x1 + x2) / 2
            my = ly if ly is not None else (y1 + y2) / 2 - 8
            self.text(mx, my, label, size=12.5, fill=MUTED, anchor="middle")

    def path(self, d: str, label="", lx=0, ly=0, dash=False, color=LINE) -> None:
        da = ' stroke-dasharray="6 5"' if dash else ""
        self.parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"{da} '
            f'marker-end="url(#head)"/>'
        )
        if label:
            self.text(lx, ly, label, size=12.5, fill=MUTED, anchor="middle")

    def legend(self, items: list[tuple[str, str]]) -> None:
        """Colour key along the bottom edge: (tone, meaning) pairs."""
        x, y = 32, self.h - 34
        self.text(x, y + 13, "Colours:", size=13, weight=700, fill=MUTED)
        x += 70
        for tone, meaning in items:
            fill, stroke = TONES[tone]
            self.parts.append(
                f'<rect x="{x}" y="{y}" width="18" height="18" rx="4" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="1.4"/>'
            )
            self.text(x + 26, y + 14, meaning, size=13, fill=MUTED)
            x += 26 + len(meaning) * 7 + 28

    def save(self, name: str) -> None:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" font-family="{FONT}" role="img">'
            f'<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
            f'markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" '
            f'fill="{LINE}"/></marker></defs>'
            f'<rect x="1" y="1" width="{self.w - 2}" height="{self.h - 2}" rx="18" fill="#ffffff" '
            f'stroke="#e5e7eb" stroke-width="2"/>'
        )
        (OUT / name).write_text(head + "".join(self.parts) + "</svg>\n", encoding="utf-8")


def workflow() -> None:
    s = Svg(1400, 600, "How autograde works",
            "You give it the exam files and it returns marks and feedback. "
            "Code double-checks everything the AI decides.")  # fmt: skip
    s.box(32, 120, 200, 70, "Question paper", [], "grey")
    s.box(32, 214, 200, 70, "Answer key", ["model answers or rubric"], "grey")
    s.box(32, 308, 200, 70, "Student answers", ["typed or photographed"], "grey")
    for y, ty in ((155, 215), (249, 250), (343, 285)):
        s.arrow(234, y, 296, ty)
    stages = [
        ("1  Read the files", ["turn the paper, key and", "answers into one item", "per student answer"], "intake/", "purple"),
        ("2  Write a scheme", ["a list of points worth", "marks for each question,", "tested before use"], "rubric.py", "blue"),
        ("3  Mark each answer", ["the AI judges each point", "and quotes the student;", "code checks the quote"], "run.py", "blue"),
        ("4  Write feedback", ["says what was good and", "what was missed, using", "only the checked marks"], "feedback.py", "green"),
    ]
    x, w, gap = 298, 190, 34
    for i, (title, ls, where, tone) in enumerate(stages):
        bx = x + i * (w + gap)
        s.box(bx, 190, w, 120, title, ls, tone)
        s.text(bx + w / 2, 336, "in " + where, size=13, fill=MUTED, anchor="middle")
        if i < 3:
            s.arrow(bx + w + 2, 250, bx + w + gap - 2, 250)
    s.box(1186, 190, 182, 120, "Results", ["marks.csv", "feedback per student", "report.html"], "green")
    s.arrow(x + 3 * (w + gap) + w + 2, 250, 1184, 250)
    s.group(298, 380, 1070, 130, "Every call to the AI goes through one gateway (the llm/ folder)", "grey")
    s.text(320, 440, "Pick the model with one setting in the config file: OpenRouter online, or the offline mock.", size=14, fill=MUTED)
    s.text(320, 468, "Every instruction given to the AI is a plain text file in prompts/, so it can be edited.", size=14, fill=MUTED)
    for i in (1, 2, 3):
        cx = x + i * (w + gap) + w / 2
        s.arrow(cx, 346, cx, 378, dash=True)
    s.legend([("grey", "what you provide"), ("purple", "reading the files"),
              ("blue", "marking"), ("green", "what you get back")])  # fmt: skip
    s.save("workflow.svg")


def app_flow() -> None:
    s = Svg(1400, 400, "Using the web app",
            "A teacher prepares and marks an exam, then publishes it. "
            "Students see only their own results.")  # fmt: skip
    steps = [
        ("Upload", ["add the paper, answer", "key and answers or scans"], "blue"),
        ("Prepare", ["a marking scheme is", "written for each question"], "blue"),
        ("Mark", ["the AI marks every answer", "in the background"], "blue"),
        ("Review", ["check flagged answers", "and change any mark"], "amber"),
        ("Publish", ["only students enrolled", "in the course can see it"], "green"),
        ("Results", ["each student sees their", "marks and feedback"], "green"),
    ]
    w, gap, x0, y = 190, 36, 32, 120
    for i, (t, ls, tone) in enumerate(steps):
        x = x0 + i * (w + gap)
        s.box(x, y, w, 110, t, ls, tone)
        s.text(x + 16, y + 24, str(i + 1), size=13, weight=700, fill=TONES[tone][1])
        if i < len(steps) - 1:
            s.arrow(x + w + 3, y + 55, x + w + gap - 3, y + 55)
    rx = x0 + 5 * (w + gap) + w / 2
    ex = x0 + 3 * (w + gap) + w / 2
    s.path(f"M {rx} {y + 113} V 290 H {ex} V {y + 113}",
           "If a student disagrees with a mark they can request a regrade, and the teacher decides",
           (rx + ex) / 2, 316, dash=True, color=TONES["red"][1])  # fmt: skip
    s.legend([("blue", "teacher prepares and marks"), ("amber", "teacher decides"),
              ("green", "students see it"), ("red", "regrade request")])  # fmt: skip
    s.save("app-flow.svg")


def architecture() -> None:
    s = Svg(1400, 1000, "Where things live in the repository",
            "Arrows show what uses what. The web app does no marking itself: it starts the "
            "command-line tool.")  # fmt: skip
    # one grid: three columns of equal boxes, rows of equal height
    cw, bh = 270, 90
    cx = (60, 420, 780)  # left edge of each column; the gaps are 90 wide
    mid = [c + cw / 2 for c in cx]  # centre of each column
    # --- how people start it
    s.group(32, 96, 678, 130, "How people use it", "purple")
    s.box(cx[0], 128, cw, 80, "Command line", ["src/autograde/cli/"], "purple")
    s.box(cx[1], 128, cw, 80, "Web app", ["app/  (Streamlit)"], "purple")
    s.arrow(cx[1] - 2, 168, cx[0] + cw + 2, 168, "starts", lx=(cx[0] + cw + cx[1]) / 2, ly=158)
    # --- the marking engine
    s.group(32, 262, 1050, 330, "The marking engine  (src/autograde/)", "blue", right=True)
    s.arrow(mid[0], 210, mid[0], 298)
    s.box(cx[0], 300, cw, bh, "intake/", ["turns exam files into", "questions and answers"], "blue")
    s.box(cx[1], 300, cw, bh, "pipeline/", ["writes the scheme, marks,", "checks, writes feedback"], "blue")
    s.box(cx[2], 300, cw, bh, "viewer/", ["builds the", "report.html page"], "blue")
    s.arrow(cx[0] + cw + 2, 345, cx[1] - 2, 345)
    s.arrow(cx[1] + cw + 2, 345, cx[2] - 2, 345, "finished marks", lx=(cx[1] + cw + cx[2]) / 2, ly=335)
    s.box(cx[0], 450, cw, bh, "ocr/", ["reads handwritten sheets", "into text"], "green")
    s.box(cx[1], 450, cw, bh, "llm/", ["one way to call", "any AI model"], "green")
    s.box(cx[2], 450, cw, bh, "prompts/", ["every instruction to", "the AI, as text files"], "green")
    s.arrow(mid[0], 448, mid[0], 392, "text for", lx=mid[0] + 44, ly=424)
    s.arrow(mid[1], 392, mid[1], 448, "asks the AI", lx=mid[1] + 50, ly=424)
    s.path(f"M {cx[1] + cw - 50} 392 V 420 H {mid[2]} V 448", "reads the instructions",
           (cx[1] + cw + mid[2]) / 2 - 10, 412)
    # --- outside services
    s.group(32, 632, 1050, 130, "Outside services", "grey")
    s.box(cx[0], 662, cw, 80, "Indic handwriting reader", ["Bodhan (optional)"], "grey")
    s.box(cx[1], 662, cw, 80, "AI models", ["OpenRouter online,", "or the offline mock"], "grey")
    s.arrow(mid[0], 542, mid[0], 660, "internet", lx=mid[0] + 36, ly=618)
    s.arrow(mid[1], 542, mid[1], 660, "internet", lx=mid[1] + 36, ly=618)
    # --- tools for testing (right column, rows aligned with the engine)
    s.group(1110, 262, 258, 330, "Tools for testing the grader", "amber")
    s.box(1130, 300, 218, bh, "evaluation/", ["measures how accurate", "and steady it is"], "amber")
    s.box(1130, 450, 218, bh, "datasets/", ["public marked answers", "(downloaded, not stored)"], "amber")
    s.arrow(1239, 392, 1239, 448, "uses", lx=1262, ly=424)
    s.arrow(1128, 345, 1086, 345, "tests", lx=1107, ly=324, dash=True)
    # --- files written while it runs
    s.text(32, 806, "Files written while it runs (none of these are stored in git)", size=14, weight=700, fill=MUTED)
    rows = [("output/runs/", ["marks, feedback and reports,", "one folder per run"]),
            ("output/rubrics/", ["saved marking schemes,", "so each is written once"]),
            ("output/logs/", ["autograde.log, a record", "of every command"]),
            ("app_data/", ["web app users and", "uploaded exams"])]  # fmt: skip
    for i, (name, lines) in enumerate(rows):
        s.box(32 + i * 262, 822, 246, 90, name, lines, "grey", tsize=15)
    s.legend([("purple", "how people start it"), ("blue", "marking engine"),
              ("green", "support code"), ("amber", "testing the grader"),
              ("grey", "outside services and files")])  # fmt: skip
    s.save("architecture.svg")


def answer_trace() -> None:
    s = Svg(1400, 1010, "What happens to one student answer",
            "Steps 3 to 7 repeat for every answer. The name on the right is the function "
            "that does the step.")  # fmt: skip
    steps = [
        ("1", "Read the teacher's files", "cmd_exam  /  intake/",
         "The question paper, answer key and student answers become one item per answer.", "purple"),
        ("2", "Get a marking scheme for the question", "RubricStore.get",
         "A list of points worth marks, written once, tested (full marks for the model answer, zero for a blank), then saved.", "purple"),
        ("3", "Let code settle what code can", "run_checks",
         "Multiple choice, numbers with units, code and figures are checked by fixed rules, not by the AI.", "blue"),
        ("4", "Read the answer by itself", "read_answer",
         "The AI first summarises what the student wrote, before comparing it with the scheme.", "blue"),
        ("5", "Judge each point", "mark_answer",
         "For every point the AI says earned, partly earned or missed, and quotes the student's own words as proof.", "blue"),
        ("6", "Check the AI's work with code", "check_grading  /  repair",
         "Is each quote really in the answer? Do the marks add up? Are the limits respected? Anything left over is flagged.", "red"),
        ("7", "Write feedback", "write_feedback",
         "Using only the checked marking: what went well and what was missed. Skipped when the answer gets full marks.", "green"),
        ("8", "Save the results", "run_items",
         "marks.csv, one file per student, schemes.md and results.jsonl, in output/runs/<name>/.", "green"),
    ]
    x, w, h, gap, y0 = 120, 1000, 84, 22, 100
    ys = [y0 + i * (h + gap) for i in range(len(steps))]
    for (n, title, fn, desc, tone), y in zip(steps, ys):
        fill, stroke = TONES[tone]
        s.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" '
                       f'stroke="{stroke}" stroke-width="1.6"/>')
        s.parts.append(f'<circle cx="{x - 44}" cy="{y + h / 2}" r="20" fill="{stroke}"/>')
        s.text(x - 44, y + h / 2 + 6, n, size=18, weight=700, fill="#ffffff", anchor="middle")
        s.text(x + 24, y + 34, title, size=18, weight=700)
        s.text(x + 24, y + 62, desc, size=14, fill=MUTED)
        cw = len(fn) * 8.4 + 28
        s.parts.append(f'<rect x="{x + w - cw - 20}" y="{y + 12}" width="{cw}" height="30" rx="15" '
                       f'fill="#ffffff" stroke="{stroke}" stroke-width="1.2"/>')
        s.parts.append(f'<text x="{x + w - cw / 2 - 20}" y="{y + 32}" font-size="13.5" '
                       f'font-family="Consolas, Menlo, monospace" fill="{INK}" '
                       f'text-anchor="middle">{escape(fn)}</text>')
        if n != "8":
            s.arrow(x + w / 2, y + h + 2, x + w / 2, y + h + gap - 2)
    top, bottom = ys[2] - 14, ys[6] + h + 14
    s.group(x - 16, top, w + 32, bottom - top, "", "grey")
    s.text(x + w + 30, top + 6, "Repeated for", size=13, weight=700, fill=MUTED)
    s.text(x + w + 30, top + 24, "every answer, several", size=13, fill=MUTED)
    s.text(x + w + 30, top + 42, "at a time. A run that", size=13, fill=MUTED)
    s.text(x + w + 30, top + 60, "stops can be resumed.", size=13, fill=MUTED)
    rx = x + w + 16
    s.path(f"M {rx} {ys[5] + h / 2} H {rx + 40} V {ys[4] + h / 2} H {rx + 2}",
           color=TONES["red"][1], dash=True)
    s.text(rx + 50, ys[4] + h + 8, "If a check fails:", size=13, fill=TONES["red"][1])
    s.text(rx + 50, ys[4] + h + 26, "redo step 5 once,", size=13, fill=TONES["red"][1])
    s.text(rx + 50, ys[4] + h + 44, "then repair it.", size=13, fill=TONES["red"][1])
    s.legend([("purple", "set-up, once per exam"), ("blue", "marking, per answer"),
              ("red", "checked by code"), ("green", "output")])  # fmt: skip
    s.save("answer-trace.svg")


def ocr_fallback() -> None:
    s = Svg(1400, 840, "Reading handwritten answer sheets",
            "You choose the main reader and the fallbacks. They are tried in order until "
            "one gives a clean result.")  # fmt: skip
    mx, mw = 32, 560
    s.box(mx, 100, mw, 64, "Photos of the answer sheet", ["one image per page"], "grey")
    s.box(mx, 210, mw, 120, "Step 1: the main reader",
          ["you choose it: ocr.reader in configs/exam.yaml",
           "default: Gemini 3.1 Flash-Lite, through OpenRouter",
           "a clean result is used straight away"], "blue")
    s.box(mx, 400, mw, 160, "Step 2: the fallbacks, in order",
          ["tried only if the step before was passed over",
           "default 1: Gemini 3.5 Flash-Lite, through OpenRouter",
           "default 2: Bodhan IndicOCR, a specialist for Indian scripts",
           "you can add, remove or reorder them: ocr.fallbacks"], "blue")
    s.box(mx, 630, mw, 90, "The text for the sheet",
          ["from the first clean reader, so each sheet", "records which reader produced it"], "green")
    s.arrow(mx + mw / 2, 166, mx + mw / 2, 208)
    s.arrow(mx + mw / 2, 332, mx + mw / 2, 398, "passed over", lx=mx + mw / 2 + 52, ly=370)
    s.arrow(mx + mw / 2, 562, mx + mw / 2, 628, "first clean result", lx=mx + mw / 2 + 70, ly=600)
    # a clean main reader skips the fallbacks
    s.path(f"M {mx + mw + 2} 270 H 626 V 675 H {mx + mw + 4}", "clean", 653, 470,
           color=TONES["green"][1])  # fmt: skip
    # side panels
    s.box(680, 100, 688, 210, "A reader is passed over when",
          ["it fails or returns an error", "it reads nothing",
           "over 25% of the words are marked as uncertain",
           "one word fills over 40% of a long page (the reader is stuck)"], "amber")
    s.box(680, 340, 688, 130, "If no reader gives a clean result",
          ["the least doubtful read is kept, and the sheet is marked as degraded in scan.json",
           "if every reader fails, the sheet is reported as failed",
           "run the command again to retry only those sheets"], "red")
    s.box(680, 500, 688, 220, "What each reader needs and costs", [
          "openrouter:  OPENROUTER_API_KEY. Paid models are allowed; a run stops",
          "if the cost OpenRouter reports passes $1 (raise it with AUTOGRADE_OCR_CAP_USD)",
          "bodhan:  INDIC_OCR_API_KEY. About Rs 0.20 an image, stops at Rs 30 a run",
          "gemini (direct):  GEMINI_API_KEY, free tier only. It may keep the images",
          "claude_cli:  your Claude Code login"], "purple")
    s.text(32, 760, "Optional: add a route to also re-read every page that looks Indic "
           "(30% or more of its letters in an Indian script), even when the main reader was clean.",
           size=13, fill=MUTED)
    s.legend([("blue", "readers"), ("amber", "when a reader is passed over"),
              ("red", "when none is clean"), ("purple", "keys and costs"),
              ("green", "result")])  # fmt: skip
    s.save("ocr-fallback.svg")


if __name__ == "__main__":
    workflow()
    app_flow()
    architecture()
    answer_trace()
    ocr_fallback()
    print("wrote", ", ".join(p.name for p in sorted(OUT.glob("*.svg"))))
