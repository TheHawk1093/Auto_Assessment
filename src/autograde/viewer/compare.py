# ruff: noqa: E501
"""One page, one tab per method, the same few answers in every tab.

Each tab embeds that run's own sample report (report_sample.html), so the detail view is the
same one used everywhere else. A first tab lays the methods side by side for each answer.
"""

from __future__ import annotations

import html
import json
from collections.abc import Sequence
from pathlib import Path

from autograde.schemas import Result


def _fmt(x: float | None, nd: int = 3) -> str:
    return "-" if x is None else f"{x:.{nd}f}"


def glance_table(labels: Sequence[str], samples: Sequence[Sequence[Result]]) -> str:
    """Rows: the sampled answers. Columns: teacher mark, then each method's mark."""
    base = {r.item.id: r for r in samples[0]}
    head = "".join(f"<th>{html.escape(x)}</th>" for x in labels)
    rows = []
    for id_, r in base.items():
        q = html.escape(r.item.question[:110])
        cells = []
        for sample in samples:
            hit = next((x for x in sample if x.item.id == id_), None)
            if hit is None:
                cells.append("<td>-</td>")
                continue
            gap = (hit.predicted_mark - r.item.human_mark) / r.item.max_mark
            tone = "ok" if abs(gap) <= 0.1 else ("lo" if gap < 0 else "hi")
            cells.append(f'<td class="{tone}">{hit.predicted_mark:g}</td>')
        rows.append(
            f"<tr><td class='q'>{q}</td><td><b>{r.item.human_mark:g}</b> / {r.item.max_mark:g}</td>"
            + "".join(cells)
            + "</tr>"
        )
    return (
        "<table><tr><th>Question</th><th>Teacher</th>" + head + "</tr>" + "".join(rows) + "</table>"
        "<p class='hint'>Green: within 10% of the total marks of the teacher's mark. "
        "Blue: stricter than the teacher. Orange: more generous.</p>"
    )


def stats_line(run_dir: Path) -> str:
    out = []
    try:
        m = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))["overall"]
        out += [
            f"error {_fmt(m.get('mean_abs_error'))}",
            f"bias {_fmt(m.get('bias'), 2)}",
            f"r {_fmt(m.get('pearson'), 2)}",
            f"qwk {_fmt(m.get('qwk'), 2)}",
            f"{m.get('n')} answers scored",
        ]
    except (OSError, KeyError, ValueError):
        pass
    try:
        u = json.loads((run_dir / "usage.json").read_text(encoding="utf-8"))
        out.append(f"cost ${u.get('cost_usd', 0):.2f}")
    except (OSError, ValueError):
        pass
    return " | ".join(out)


def write_compare(
    tabs: Sequence[tuple[str, str, Path]],
    samples: Sequence[Sequence[Result]],
    out_path: Path,
    title: str,
) -> Path:
    """tabs: (label, one-line description, run folder). Sample reports must already be built."""
    labels = [t[0] for t in tabs]
    buttons = ['<button class="on" data-t="glance">Side by side</button>'] + [
        f'<button data-t="t{i}">{html.escape(lab)}</button>' for i, (lab, _, _) in enumerate(tabs)
    ]
    panes = [f'<section id="glance" class="pane on">{glance_table(labels, samples)}</section>']
    for i, (lab, desc, run_dir) in enumerate(tabs):
        src = Path("..") / run_dir.name / "report_sample.html"
        panes.append(
            f'<section id="t{i}" class="pane"><div class="meta"><b>{html.escape(lab)}</b>: '
            f"{html.escape(desc)}<br><span>{html.escape(stats_line(run_dir))} "
            f"(numbers cover the whole run, not just these answers)</span></div>"
            f'<iframe data-src="{src.as_posix()}" title="{html.escape(lab)}"></iframe></section>'
        )
    page = _PAGE.replace("{{TITLE}}", html.escape(title))
    page = page.replace("{{BUTTONS}}", "".join(buttons)).replace("{{PANES}}", "".join(panes))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")
    return out_path


_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{{TITLE}}</title>
<style>
:root{--bg:#fff;--ink:#1b1b1f;--muted:#666;--line:#ddd;--surface:#f6f6f8;--ok:#e3f4e6;--lo:#e2ecfb;--hi:#fdebd6;--accent:#2457c5}
@media (prefers-color-scheme:dark){:root{--bg:#16161a;--ink:#ececf0;--muted:#9a9aa5;--line:#34343c;--surface:#202026;--ok:#1e3a26;--lo:#1f2f4d;--hi:#4a3418;--accent:#7aa2ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,sans-serif}
header{padding:14px 16px 0}h1{font-size:18px;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 10px}
nav{display:flex;flex-wrap:wrap;gap:4px;padding:0 16px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:2}
nav button{border:1px solid var(--line);border-bottom:none;background:var(--surface);color:var(--ink);padding:8px 12px;border-radius:6px 6px 0 0;cursor:pointer;font:inherit}
nav button.on{background:var(--bg);color:var(--accent);font-weight:600;box-shadow:inset 0 2px 0 var(--accent)}
.pane{display:none;padding:12px 16px}.pane.on{display:block}
.meta{padding:8px 10px;background:var(--surface);border:1px solid var(--line);margin-bottom:8px}.meta span{color:var(--muted)}
iframe{width:100%;height:calc(100vh - 190px);min-height:480px;border:1px solid var(--line);background:#fff}
table{border-collapse:collapse;width:100%}th,td{border:1px solid var(--line);padding:6px 8px;text-align:center}
td.q{text-align:left;max-width:380px}td.ok{background:var(--ok)}td.lo{background:var(--lo)}td.hi{background:var(--hi)}
.hint{color:var(--muted)}
</style></head><body>
<header><h1>{{TITLE}}</h1><p class="sub">The same answers in every tab. Open a tab to read the question, answer, marking and feedback for that method.</p></header>
<nav>{{BUTTONS}}</nav>{{PANES}}
<script>
document.querySelectorAll("nav button").forEach(function(b){b.onclick=function(){
document.querySelectorAll("nav button,.pane").forEach(function(x){x.classList.remove("on")});
b.classList.add("on");var p=document.getElementById(b.dataset.t);p.classList.add("on");
var f=p.querySelector("iframe");if(f&&!f.src)f.src=f.dataset.src;}});
</script></body></html>
"""
