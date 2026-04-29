"""utils/light_theme.py — Clean Light Theme for DIP Learning Simulator."""

LIGHT_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Poppins:wght@400;500;600;700;800&display=swap');

:root {
  --bg-page:     #f0f4ff;
  --bg-surface:  #ffffff;
  --bg-card:     #ffffff;
  --bg-sidebar:  #f8faff;
  --border:      rgba(99, 120, 220, 0.18);
  --border-hi:   rgba(99, 120, 220, 0.45);
  --accent-blue: #4361ee;
  --accent-cyan: #4cc9f0;
  --accent-purple:#7209b7;
  --accent-green: #06d6a0;
  --accent-amber: #f8961e;
  --accent-red:   #ef233c;
  --text-hi:     #1a1a2e;
  --text-mid:    #4a5568;
  --text-lo:     #9aa3b7;
  --shadow-sm:   0 2px 8px rgba(67,97,238,0.08), 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md:   0 8px 24px rgba(67,97,238,0.12), 0 2px 8px rgba(0,0,0,0.06);
  --shadow-lg:   0 16px 40px rgba(67,97,238,0.16), 0 4px 12px rgba(0,0,0,0.08);
}

/* ── GLOBAL RESET ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background: var(--bg-page) !important;
  color: var(--text-hi) !important;
  -webkit-font-smoothing: antialiased;
}

.stApp {
  background:
    radial-gradient(ellipse at 10% 10%, rgba(67,97,238,0.06) 0%, transparent 60%),
    radial-gradient(ellipse at 90% 90%, rgba(114,9,183,0.05) 0%, transparent 60%),
    var(--bg-page) !important;
  min-height: 100vh !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background: var(--bg-sidebar) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 20px rgba(67,97,238,0.08) !important;
}
section[data-testid="stSidebar"] * { color: var(--text-hi) !important; }
section[data-testid="stSidebar"] .stSelectbox > label,
section[data-testid="stSidebar"] .stSlider > label {
  color: var(--text-mid) !important;
  font-size: 0.82rem !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 16px !important;
  box-shadow: var(--shadow-md) !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-2px) !important;
  box-shadow: var(--shadow-lg) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-mid) !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  color: var(--accent-blue) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.4rem !important;
}

/* ── BUTTONS ── */
.stButton button {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)) !important;
  color: white !important;
  border: none !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 0.55rem 1.6rem !important;
  border-radius: 10px !important;
  transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
  box-shadow: 0 4px 15px rgba(67,97,238,0.35) !important;
}
.stButton button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(67,97,238,0.45) !important;
}
.stButton button:active {
  transform: translateY(0) !important;
}
.stDownloadButton button {
  background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan)) !important;
  box-shadow: 0 4px 15px rgba(6,214,160,0.35) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--text-mid) !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  border-radius: 8px !important;
  padding: 7px 16px !important;
  transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)) !important;
  color: white !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 12px rgba(67,97,238,0.35) !important;
}

/* ── SLIDERS ── */
.stSlider > div > div > div { background: rgba(67,97,238,0.15) !important; border-radius: 4px !important; }
.stSlider > div > div > div > div {
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)) !important;
  box-shadow: 0 0 8px rgba(67,97,238,0.4) !important;
}

/* ── SELECT BOXES ── */
.stSelectbox > div > div {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-hi) !important;
  border-radius: 10px !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  background: var(--bg-card) !important;
  border: 2px dashed var(--border-hi) !important;
  border-radius: 14px !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div {
  background: rgba(67,97,238,0.12) !important;
  border-radius: 6px !important;
}
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan), var(--accent-purple)) !important;
  border-radius: 6px !important;
}

/* ── HEADINGS ── */
h1 { font-family: 'Poppins', sans-serif !important; color: var(--text-hi) !important; font-weight: 800 !important; }
h2, h3, h4 { font-family: 'Poppins', sans-serif !important; color: var(--text-hi) !important; font-weight: 700 !important; }
hr { border-color: var(--border) !important; }
.stCaption { color: var(--text-lo) !important; }

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
  background: var(--bg-card) !important;
  color: var(--text-hi) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  box-shadow: var(--shadow-sm) !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
  border-color: var(--accent-blue) !important;
  box-shadow: 0 0 0 3px rgba(67,97,238,0.15) !important;
}

/* ── FORMS ── */
[data-testid="stForm"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  box-shadow: var(--shadow-md) !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
  background: var(--bg-card) !important;
  border-radius: 10px !important;
  border: 1px solid var(--border) !important;
}

/* ── ALERTS ── */
.stSuccess { background: rgba(6,214,160,0.1) !important; border: 1px solid rgba(6,214,160,0.4) !important; border-radius: 10px !important; }
.stInfo    { background: rgba(76,201,240,0.1) !important; border: 1px solid rgba(76,201,240,0.4) !important; border-radius: 10px !important; }
.stWarning { background: rgba(248,150,30,0.1) !important; border: 1px solid rgba(248,150,30,0.4) !important; border-radius: 10px !important; }
.stError   { background: rgba(239,35,60,0.1)  !important; border: 1px solid rgba(239,35,60,0.4)  !important; border-radius: 10px !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-page); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--accent-blue), var(--accent-purple)); border-radius: 4px; }

/* ── RADIO / CHECKBOX ── */
.stRadio label, .stCheckbox label { color: var(--text-hi) !important; }

/* ── IMAGES ── */
img { border-radius: 10px !important; }
[data-testid="stImage"] img {
  box-shadow: var(--shadow-md) !important;
}

/* ── TOOL CARDS (override stButton for tool card style) ── */
.tool-btn > button {
  background: white !important;
  color: var(--text-hi) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 14px !important;
  width: 100% !important;
  text-align: left !important;
  padding: 14px 16px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.25s !important;
  font-family: 'Inter', sans-serif !important;
}
.tool-btn > button:hover {
  border-color: var(--accent-blue) !important;
  box-shadow: var(--shadow-md), 0 0 0 3px rgba(67,97,238,0.1) !important;
  transform: translateY(-3px) !important;
  background: rgba(67,97,238,0.03) !important;
}
</style>
"""

LIGHT_BG_PATTERNS = """
<div style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;
     background-image:
       radial-gradient(circle at 20% 20%, rgba(67,97,238,0.06) 0%, transparent 50%),
       radial-gradient(circle at 80% 80%, rgba(114,9,183,0.05) 0%, transparent 50%),
       radial-gradient(circle at 60% 10%, rgba(76,201,240,0.04) 0%, transparent 40%);
">
</div>
<div style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;
     background-image:linear-gradient(rgba(67,97,238,0.025) 1px,transparent 1px),
     linear-gradient(90deg,rgba(67,97,238,0.025) 1px,transparent 1px);
     background-size:60px 60px;
     mask-image:linear-gradient(to bottom,transparent 0%,rgba(0,0,0,0.4) 30%,rgba(0,0,0,0.4) 70%,transparent 100%)">
</div>
"""

def inject_light(title="DIP Learning Simulator v4", icon="🔬"):
    """Inject the light theme into a Streamlit page."""
    import streamlit as st
    st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)
    st.markdown(LIGHT_BG_PATTERNS, unsafe_allow_html=True)
