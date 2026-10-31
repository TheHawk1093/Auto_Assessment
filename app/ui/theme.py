"""The look of the app: one stylesheet, injected once.

Colours are neutral overlays and `currentColor`, so it reads the same in Streamlit's light and
dark themes. If a Streamlit update renames an internal element, the rule stops matching and
the page falls back to the default look; nothing depends on it. Edit CSS here; classes
starting `ag-` are used by `ui/components.py`.
"""

from __future__ import annotations

import streamlit as st

ACCENT = "#4f46e5"  # also primaryColor in .streamlit/config.toml

CSS = """
:root {
  --ag-line: rgba(128, 128, 128, .28);
  --ag-soft: rgba(128, 128, 128, .08);
  --ag-accent: #4f46e5;
  --ag-radius: 14px;
}
.block-container { padding-top: 2.4rem; max-width: 1180px; }
header[data-testid="stHeader"] { background: transparent; }
footer, .stDeployButton, #MainMenu { visibility: hidden; height: 0; }
h1, h2, h3 { letter-spacing: -0.01em; }
section[data-testid="stSidebar"] { border-right: 1px solid var(--ag-line); }

/* cards */
[data-testid="stMetric"] {
  background: var(--ag-soft); border: 1px solid var(--ag-line);
  border-radius: var(--ag-radius); padding: 14px 18px;
}
[data-testid="stMetricLabel"] p { opacity: .7; font-size: .85rem; }
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: var(--ag-radius); }
[data-testid="stExpander"] { border-radius: var(--ag-radius); }
[data-testid="stForm"] { border-radius: var(--ag-radius); }

/* controls */
.stButton > button, .stDownloadButton > button { border-radius: 10px; font-weight: 600; }
button[data-baseweb="tab"] { font-weight: 600; }

/* chips */
.ag-chip {
  display: inline-block; padding: 2px 10px; margin: 0 6px 4px 0; border-radius: 999px;
  font-size: .78rem; font-weight: 600; line-height: 1.6; border: 1px solid transparent;
}
.ag-chip.neutral { background: var(--ag-soft); border-color: var(--ag-line); }
.ag-chip.blue    { background: rgba(59, 130, 246, .16); border-color: rgba(59, 130, 246, .4); }
.ag-chip.green   { background: rgba(34, 197, 94, .16);  border-color: rgba(34, 197, 94, .4); }
.ag-chip.amber   { background: rgba(245, 158, 11, .18); border-color: rgba(245, 158, 11, .45); }
.ag-chip.red     { background: rgba(239, 68, 68, .16);  border-color: rgba(239, 68, 68, .4); }
.ag-chip.violet  { background: rgba(139, 92, 246, .16); border-color: rgba(139, 92, 246, .4); }

/* page header */
.ag-head h1 { margin: 0 0 .15rem 0; font-size: 2rem; }
.ag-head p { margin: 0 0 .5rem 0; opacity: .7; }

/* stepper */
.ag-steps { display: flex; gap: 0; margin: .6rem 0 1.2rem 0; flex-wrap: wrap; }
.ag-step { flex: 1 1 120px; display: flex; align-items: center; gap: 8px; padding: 6px 4px; min-width: 120px; }
.ag-step .dot {
  width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center;
  font-size: .8rem; font-weight: 700; border: 2px solid var(--ag-line); flex: none;
}
.ag-step.done .dot { background: #22c55e; border-color: #22c55e; color: #fff; }
.ag-step.current .dot { background: var(--ag-accent); border-color: var(--ag-accent); color: #fff; }
.ag-step .name { font-size: .85rem; font-weight: 600; opacity: .55; }
.ag-step.done .name, .ag-step.current .name { opacity: 1; }
.ag-step .badge { margin-left: 4px; }

/* score card and mark bars */
.ag-score { border: 1px solid var(--ag-line); background: var(--ag-soft);
  border-radius: 18px; padding: 22px 26px; margin-bottom: 1rem; }
.ag-score .big { font-size: 3rem; font-weight: 800; line-height: 1; letter-spacing: -0.02em; }
.ag-score .of { font-size: 1.2rem; opacity: .6; font-weight: 600; }
.ag-score .label { opacity: .7; font-weight: 600; margin-bottom: 6px; }
.ag-bar { height: 8px; border-radius: 999px; background: var(--ag-line); overflow: hidden; margin-top: 12px; }
.ag-bar > span { display: block; height: 100%; border-radius: 999px; background: var(--ag-accent); }
.ag-bar.good > span { background: #22c55e; }
.ag-bar.mid > span { background: #f59e0b; }
.ag-bar.low > span { background: #ef4444; }

/* exam cards */
.ag-card-title { font-size: 1.1rem; font-weight: 700; margin: 0 0 .25rem 0; }
.ag-card-meta { opacity: .65; font-size: .85rem; margin-bottom: .4rem; }
"""


def inject() -> None:
    """Add the stylesheet to the page."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
