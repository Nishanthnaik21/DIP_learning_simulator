"""app.py — DIP Learning Simulator Home Dashboard (3D + Theme Toggle + DB)."""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="DIP Learning Simulator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Theme injection ───────────────────────────────────────────────────────────
from utils.theme_manager import inject_theme, theme_toggle_button, get_theme
inject_theme()

# ── Session init ──────────────────────────────────────────────────────────────
for k, v in [("session_ops", 0), ("quiz_history", {}),
             ("session_start", datetime.now().strftime("%H:%M")),
             ("theme", "light")]:
    if k not in st.session_state:
        st.session_state[k] = v

quiz_total   = sum(st.session_state["quiz_history"].values())
quiz_max     = len(st.session_state["quiz_history"]) * 5
current_user = st.session_state.get("current_user", "User")
user_role    = st.session_state.get("user_role", "student")
theme        = get_theme()

IS_DARK = theme == "dark"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if IS_DARK:
        card_bg = "rgba(10,30,70,0.7)"
        card_border = "rgba(0,168,255,0.25)"
        name_color = "#00a8ff"
        role_color = "#8ab4d4"
    else:
        card_bg = "rgba(67,97,238,0.06)"
        card_border = "rgba(67,97,238,0.18)"
        name_color = "#4361ee"
        role_color = "#6b7280"

    st.markdown(f"""
    <div style="background:{card_bg};border:1px solid {card_border};border-radius:14px;
                padding:16px 18px;margin:8px 0 16px 0">
      <div style="font-size:0.68rem;color:{role_color};text-transform:uppercase;
                  letter-spacing:0.12em;margin-bottom:4px;font-weight:500">Logged in as</div>
      <div style="font-size:1.05rem;font-weight:700;color:{name_color}">
        👤 {current_user.capitalize()}
      </div>
      <div style="font-size:0.72rem;color:{role_color};margin-top:2px;text-transform:capitalize">
        {user_role}
      </div>
    </div>
    """, unsafe_allow_html=True)

    theme_toggle_button()

# ─────────────────────────────────────────────────────────────────────────────
# THEME-AWARE COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
if IS_DARK:
    HERO_SUBTITLE   = "rgba(138,180,212,0.7)"
    BADGE_BG        = "rgba(0,168,255,0.1)"
    BADGE_BORDER    = "rgba(0,168,255,0.25)"
    CARD_BG         = "rgba(10,25,60,0.55)"
    CARD_SURFACE    = "rgba(10,30,70,0.6)"
    STAT_BG         = "rgba(10,30,70,0.55)"
    SECTION_COLOR   = "#00a8ff"
    SECTION_DIV     = "rgba(0,168,255,0.4)"
    FOOTER_COLOR    = "rgba(58,90,122,0.8)"
    TOOL_BG         = "rgba(10,25,60,0.45)"
    STEP_BG         = "rgba(10,25,60,0.45)"
    TEXT_MAIN       = "#e8f4ff"
    TEXT_SUB        = "#8ab4d4"
    TEXT_LO         = "#3a5a7a"
    FONT_HERO       = "'Orbitron', monospace"
    FONT_CARD       = "'JetBrains Mono', monospace"
else:
    HERO_SUBTITLE   = "#5698a1"
    BADGE_BG        = "rgba(85,201,212,0.08)"
    BADGE_BORDER    = "rgba(85,201,212,0.25)"
    CARD_BG         = "#ffffff"
    CARD_SURFACE    = "#ffffff"
    STAT_BG         = "#f5fdfd"
    SECTION_COLOR   = "#2baebf"
    SECTION_DIV     = "rgba(85,201,212,0.35)"
    FOOTER_COLOR    = "#80b2b8"
    TOOL_BG         = "#ffffff"
    STEP_BG         = "#ffffff"
    TEXT_MAIN       = "#0a2f35"
    TEXT_SUB        = "#3d676d"
    TEXT_LO         = "#759fa5"
    FONT_HERO       = "'Poppins', sans-serif"
    FONT_CARD       = "'Inter', sans-serif"

ACCENTS = ["#55c9d4","#6cd1db","#4ac5d4","#7edde6","#2baebf","#3aa5b3"] if not IS_DARK else \
          ["#00a8ff","#b44fff","#00fff5","#00ff9d","#ffb700","#ff3366"]

# ─────────────────────────────────────────────────────────────────────────────
# 3D ANIMATED HERO SECTION
# ─────────────────────────────────────────────────────────────────────────────
hero_bg = "linear-gradient(135deg,#020818,#050f28)" if IS_DARK else "linear-gradient(135deg,#e6fbfd,#ffffff)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=JetBrains+Mono:wght@400;600&family=Poppins:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* ── ANIMATED 3D HERO ── */
.hero-3d-wrap {{
  text-align:center;
  padding: 40px 0 32px 0;
  position: relative;
}}
/* Floating micro-orbs in hero */
.hero-orb {{
  position:absolute;width:180px;height:180px;border-radius:50%;
  filter:blur(70px);pointer-events:none;
}}
.hero-orb1 {{
  background:{'rgba(0,168,255,0.12)' if IS_DARK else 'rgba(85,201,212,0.15)'};
  top:-20px;left:5%;animation:hero-drift 8s ease-in-out infinite;
}}
.hero-orb2 {{
  background:{'rgba(180,79,255,0.10)' if IS_DARK else 'rgba(136,226,235,0.15)'};
  top:0;right:5%;animation:hero-drift 10s ease-in-out infinite reverse;
}}
@keyframes hero-drift {{
  0%,100%{{transform:translateY(0)}}
  50%{{transform:translateY(-20px)}}
}}

/* ── SPINNING 3D BADGE ── */
.badge-3d-scene {{
  width:100px;height:100px;perspective:500px;
  margin:0 auto 24px auto;
}}
.badge-3d {{
  width:100px;height:100px;
  background:{'linear-gradient(135deg,rgba(0,100,255,0.5),rgba(100,0,200,0.5))' if IS_DARK else 'linear-gradient(135deg,rgba(85,201,212,0.8),rgba(136,226,235,0.8))'};
  border-radius:24px;
  border:{'1.5px solid rgba(0,168,255,0.4)' if IS_DARK else '1.5px solid rgba(85,201,212,0.4)'};
  box-shadow:{'0 0 40px rgba(0,168,255,0.3),0 20px 40px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.1)' if IS_DARK else '0 20px 40px rgba(85,201,212,0.25),0 0 40px rgba(85,201,212,0.1),inset 0 1px 0 rgba(255,255,255,0.6)'};
  display:flex;align-items:center;justify-content:center;font-size:2.6rem;
  transform:perspective(500px) rotateY(0deg);
  animation:badge-spin 6s ease-in-out infinite;
  backdrop-filter:blur(10px);
  transition:all 0.3s;
}}
@keyframes badge-spin {{
  0%,100%{{transform:perspective(500px) rotateY(-15deg) rotateX(5deg) scale(1)}}
  25%{{transform:perspective(500px) rotateY(15deg) rotateX(-5deg) scale(1.05)}}
  50%{{transform:perspective(500px) rotateY(15deg) rotateX(10deg) scale(1)}}
  75%{{transform:perspective(500px) rotateY(-15deg) rotateX(-8deg) scale(1.03)}}
}}

/* ── HERO TITLE ── */
.hero-title-main {{
  font-family:{FONT_HERO};
  font-size:clamp(1.8rem,4vw,2.9rem);
  font-weight:800;
  line-height:1.1;
  letter-spacing:{'0.03em' if IS_DARK else '-0.01em'};
  background:{'linear-gradient(135deg,#00a8ff,#00fff5,#b44fff,#00ff9d)' if IS_DARK else 'linear-gradient(135deg,#2baebf,#75d5e0,#2baebf)'};
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
  filter:{'drop-shadow(0 0 24px rgba(0,168,255,0.35))' if IS_DARK else 'none'};
  animation: title-glow 3s ease-in-out infinite;
  margin-bottom:10px;
}}
@keyframes title-glow {{
  0%,100%{{filter:{'drop-shadow(0 0 20px rgba(0,168,255,0.3))' if IS_DARK else 'none'}}}
  50%{{filter:{'drop-shadow(0 0 40px rgba(0,168,255,0.5))' if IS_DARK else 'none'}}}
}}

/* ── STAT CARDS ── */
.stat-card {{
  background:{STAT_BG};
  border-radius:14px;
  padding:14px 10px;
  text-align:center;
  position:relative;
  overflow:hidden;
  transition:all 0.25s cubic-bezier(0.34,1.56,0.64,1);
  cursor:default;
}}
.stat-card:hover {{
  transform:translateY(-4px) scale(1.02) !important;
}}

/* ── MODULE + TOOL CARDS ── */
.mod-card, .tool-card {{
  border-radius:16px;
  transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  cursor:pointer;
  position:relative;
  overflow:hidden;
}}
.mod-card:hover  {{ transform:translateY(-6px) scale(1.02) !important; }}
.tool-card:hover {{ transform:translateY(-4px) scale(1.01) !important; }}

/* ── STEP CARDS ── */
.step-card {{
  border-radius:14px;
  padding:14px 10px;
  text-align:center;
  transition:all 0.25s;
}}

/* ── STAGGERED ENTRANCE ANIMATIONS ── */
@keyframes slide-up {{
  from{{opacity:0;transform:translateY(30px)}}
  to  {{opacity:1;transform:translateY(0)}}
}}
.anim-1{{animation:slide-up 0.5s 0.05s both}}
.anim-2{{animation:slide-up 0.5s 0.10s both}}
.anim-3{{animation:slide-up 0.5s 0.15s both}}
.anim-4{{animation:slide-up 0.5s 0.20s both}}
.anim-5{{animation:slide-up 0.5s 0.25s both}}
</style>
""", unsafe_allow_html=True)

# ── Hero HTML ──────────────────────────────────────────────────────────────────
badges = [
    ("OpenCV 4.8", ACCENTS[0]), ("NumPy", ACCENTS[2]), ("Streamlit", ACCENTS[1]),
    ("ReportLab", ACCENTS[3]), ("Railway MySQL", ACCENTS[4])
]
badge_html = "".join([
    f'<span style="background:{BADGE_BG};border:1px solid {c}44;color:{c};'
    f'border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:600;'
    f'margin:3px;display:inline-block;letter-spacing:0.04em">{n}</span>'
    for n, c in badges
])

st.markdown(f"""
<div class="hero-3d-wrap">
  <div class="hero-orb hero-orb1"></div>
  <div class="hero-orb hero-orb2"></div>
  <div style="font-size:0.72rem;color:{HERO_SUBTITLE};letter-spacing:0.3em;
              text-transform:uppercase;margin-bottom:16px;font-weight:500">
    DIP SIMULATOR &nbsp;·&nbsp; DIGITAL IMAGE PROCESSING
  </div>
  <div class="badge-3d-scene">
    <div class="badge-3d">🔬</div>
  </div>
  <div class="hero-title-main">DIP LEARNING<br>SIMULATOR</div>
  <div style="font-size:0.85rem;color:{HERO_SUBTITLE};margin-bottom:20px">
    24 Pages &nbsp;·&nbsp; 19 Tools &nbsp;·&nbsp; Dark/Light Theme
  </div>
  <div style="display:flex;justify-content:center;flex-wrap:wrap;gap:4px">
    {badge_html}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats Row ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
stats = [
    (c1, "🛠️ Operations",   str(st.session_state["session_ops"]),           ACCENTS[0]),
    (c2, "🧠 Quiz Score",   f"{quiz_total}/{quiz_max}" if quiz_max else "—", ACCENTS[1]),
    (c3, "📚 Modules Done", f"{len(st.session_state['quiz_history'])}/5",    ACCENTS[2]),
    (c4, "🕐 Started",      st.session_state["session_start"],               ACCENTS[3]),
    (c5, "📦 Pages",        "24",                                            ACCENTS[4]),
    (c6, "⚡ Pages",        "24",                                            ACCENTS[5]),
]
for i, (col, label, val, color) in enumerate(stats):
    border_extra = f"box-shadow:0 0 12px {color}22;" if IS_DARK else f"box-shadow:0 4px 20px {color}10;"
    top_line = f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{color},{color}44)"></div>' if IS_DARK else \
               f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{color},{color}44);border-radius:14px 14px 0 0"></div>'
    with col:
        col.markdown(f"""
        <div class="stat-card anim-{i+1}" style="border:1px solid {color}22;{border_extra}">
          {top_line}
          <div style="font-size:0.65rem;color:{TEXT_LO};letter-spacing:0.12em;text-transform:uppercase;
                      margin-bottom:6px;font-weight:500">{label}</div>
          <div style="font-family:{FONT_CARD};font-size:1.3rem;font-weight:700;
                      color:{color};{'text-shadow:0 0 10px '+color+'66;' if IS_DARK else ''}">{val}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Section header helper ─────────────────────────────────────────────────────
def section_header(text, color=None):
    c = color or SECTION_COLOR
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:18px">
      <div style="width:4px;height:22px;background:linear-gradient(180deg,{c},{c}44);
                  border-radius:2px;{'box-shadow:0 0 8px '+c+'66;' if IS_DARK else ''}"></div>
      <div style="font-family:{FONT_HERO};font-size:{'0.7rem' if IS_DARK else '0.82rem'};font-weight:700;
                  color:{c};letter-spacing:0.2em;text-transform:uppercase;
                  {'text-shadow:0 0 12px '+c+'44;' if IS_DARK else ''}">
        {text}
      </div>
      <div style="flex:1;height:1px;background:linear-gradient(90deg,{c}44,transparent)"></div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# COURSE MODULES
# ─────────────────────────────────────────────────────────────────────────────
section_header("Course Modules", ACCENTS[0])

modules = [
    {"n":"01","icon":"🖼️","title":"Image\nFundamentals",
     "topics":["Pixel Inspector","Sampling","Quantization","Channels","Statistics"],
     "c":ACCENTS[0],"page":"pages/1_Module1_Fundamentals.py"},
    {"n":"02","icon":"📡","title":"Spatial &\nFrequency",
     "topics":["Histogram EQ","CLAHE","Smoothing","Sharpening","DFT","Freq Filters"],
     "c":ACCENTS[1],"page":"pages/2_Module2_SpatialFrequency.py"},
    {"n":"03","icon":"🔧","title":"Image\nRestoration",
     "topics":["Noise Models","Inverse Filter","Wiener","CLS Filter","PSNR/SSIM"],
     "c":ACCENTS[2],"page":"pages/3_Module3_Restoration.py"},
    {"n":"04","icon":"🎨","title":"Color, Wavelets\n& Morphology",
     "topics":["Color Models","Pseudo-Color","Wavelets","Morph Ops","Hit-or-Miss"],
     "c":ACCENTS[4],"page":"pages/4_Module4_ColorMorphology.py"},
    {"n":"05","icon":"✂️","title":"Image\nSegmentation",
     "topics":["Edge Detection","Hough Transform","Thresholding","Corners","Descriptors"],
     "c":ACCENTS[5],"page":"pages/5_Module5_Segmentation.py"},
]

mod_cols = st.columns(5)
for col, m in zip(mod_cols, modules):
    pills = "".join([
        f'<span style="background:{m["c"]}13;color:{m["c"]}bb;border:1px solid {m["c"]}22;'
        f'border-radius:20px;padding:2px 8px;font-size:0.68rem;margin:2px 1px;display:inline-block;font-weight:500">'
        f'{t}</span>' for t in m["topics"]
    ])
    shadow = f"0 4px 20px {m['c']}18,0 0 20px {m['c']}11" if IS_DARK else f"0 4px 20px {m['c']}12"
    border = f"{m['c']}22" if IS_DARK else f"{m['c']}18"
    with col:
        st.markdown(f"""
        <div class="mod-card" style="background:{CARD_SURFACE};border:1.5px solid {border};
                    height:215px;padding:18px 14px;
                    box-shadow:{shadow}" 
             onmouseover="this.style.borderColor='{m['c']}55';this.style.boxShadow='0 16px 40px {m['c']}22'"
             onmouseout="this.style.borderColor='{border}';this.style.boxShadow='{shadow}'">
          <div style="position:absolute;top:0;left:0;right:0;height:3px;
                      background:linear-gradient(90deg,{m['c']},{m['c']}44);
                      border-radius:16px 16px 0 0"></div>
          <div style="font-size:0.62rem;color:{m['c']}99;letter-spacing:0.12em;font-weight:600;margin-bottom:8px">
            MODULE {m['n']}
          </div>
          <div style="font-size:1.6rem;margin-bottom:6px">{m['icon']}</div>
          <div style="font-family:{'Orbitron' if IS_DARK else 'Poppins'},{'monospace' if IS_DARK else 'sans-serif'};
                      font-size:0.75rem;font-weight:700;color:{m['c']};
                      line-height:1.3;white-space:pre-line;margin-bottom:10px;
                      {'text-shadow:0 0 10px '+m['c']+'44;' if IS_DARK else ''}">
            {m['title']}
          </div>
          <div style="line-height:1.9">{pills}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"Open Module {m['n']}", key=f"mod_{m['n']}", use_container_width=True):
            st.switch_page(m["page"])

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TOOLS & FEATURES
# ─────────────────────────────────────────────────────────────────────────────
section_header("Tools & Features", ACCENTS[1])

tools = [
    ("🖼️","Sample Gallery",      "10 classic DIP images",     ACCENTS[0], "pages/6_Gallery.py"),
    ("↔️","Compare Slider",      "Drag to compare",           ACCENTS[2], "pages/7_Comparison.py"),
    ("🔭","Super Resolution",    "6 upscaling methods",       ACCENTS[1], "pages/8_SuperResolution.py"),
    ("📄","PDF Lab Report",      "Auto-generate record",      ACCENTS[4], "pages/9_LabReport.py"),
    ("🧠","Quiz Mode",           "25 MCQs + scoring",         ACCENTS[5], "pages/10_Quiz.py"),
    ("📷","Webcam Capture",      "Live camera DIP",           ACCENTS[0], "pages/11_Webcam.py"),
    ("🗜️","JPEG Compression",    "DCT block simulator",       ACCENTS[2], "pages/12_JPEG_Compression.py"),
    ("✨","GIF Animator",        "Parameter sweep GIF",       ACCENTS[1], "pages/13_GIF_Animator.py"),
    ("📦","Batch Processing",    "Multi-image pipeline",      ACCENTS[4], "pages/14_Batch_Processing.py"),
    ("💻","Code Exporter",       "Export Python code",        ACCENTS[5], "pages/15_Code_Exporter.py"),
    ("🎯","Param Challenge",     "Match the target",          ACCENTS[0], "pages/16_Parameter_Challenge.py"),
    ("📐","Feature Descriptors", "SIFT, HOG, ORB",            ACCENTS[2], "pages/17_Feature_Descriptors.py"),
    ("🌊","Optical Flow",        "Motion estimation",         ACCENTS[1], "pages/18_Optical_Flow.py"),
    ("📊","Session Recorder",    "Save & export",             ACCENTS[4], "pages/19_Session_Recorder.py"),
    ("📏","Quality Metrics",     "PSNR SSIM MSE VIF",         ACCENTS[5], "pages/20_Quality_Metrics.py"),
    ("🔍","Template Matching",   "Cross-correlation",         ACCENTS[0], "pages/21_Template_Matching.py"),
    ("📄","Doc Scanner",         "Perspective + OCR",         ACCENTS[2], "pages/22_Document_Scanner.py"),
    ("🕵️","Forgery Detector",    "ELA tampering check",       ACCENTS[1], "pages/23_Forgery_Detector.py"),
    ("🔗","Image Stitching",     "Panorama builder",          ACCENTS[4], "pages/24_Image_Stitching.py"),
]

tool_rows = [tools[i:i+5] for i in range(0, len(tools), 5)]
for row in tool_rows:
    tcols = st.columns(5)
    for col, (icon, name, desc, color, page) in zip(tcols, row):
        icon_bg   = f"linear-gradient(135deg,{color}18,{color}28)"
        card_shad = f"0 3px 12px {color}11" if not IS_DARK else f"0 3px 12px rgba(0,0,0,0.4),0 0 8px {color}11"
        card_brd  = f"{color}18"
        with col:
            st.markdown(f"""
            <div class="tool-card" style="background:{TOOL_BG};border:1.5px solid {card_brd};
                        padding:16px 12px;text-align:center;margin-bottom:4px;
                        box-shadow:{card_shad}"
                 onmouseover="this.style.borderColor='{color}55';this.style.transform='translateY(-4px) scale(1.02)';this.style.boxShadow='0 12px 28px {color}22'"
                 onmouseout="this.style.borderColor='{card_brd}';this.style.transform='';this.style.boxShadow='{card_shad}'">
              <div style="width:46px;height:46px;border-radius:13px;margin:0 auto 10px auto;
                          background:{icon_bg};display:flex;align-items:center;justify-content:center;
                          font-size:1.35rem;border:1px solid {color}22">
                {icon}
              </div>
              <div style="font-family:{'Orbitron,monospace' if IS_DARK else 'Poppins,sans-serif'};
                          font-size:0.69rem;font-weight:700;color:{TEXT_MAIN};margin-bottom:3px;
                          letter-spacing:{'0.04em' if IS_DARK else '0'}">
                {name}
              </div>
              <div style="font-size:0.67rem;color:{TEXT_LO};line-height:1.3">{desc}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"▶ {name}", key=f"tool_{name.replace(' ','_')}", use_container_width=True):
                st.switch_page(page)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# QUICK START
# ─────────────────────────────────────────────────────────────────────────────
section_header("Quick Start", ACCENTS[3])
steps = [
    ("01","Choose Image",  "Pick from 10 samples or upload your own",      ACCENTS[0]),
    ("02","Select Module", "Navigate via sidebar to any of 24 pages",      ACCENTS[1]),
    ("03","Experiment",    "Adjust sliders — see results instantly",        ACCENTS[2]),
    ("04","Compare",       "Drag-compare before/after with slider",         ACCENTS[4]),
    ("05","Export",        "Download PDF, code, GIF, or session",           ACCENTS[5]),
    ("06","Quiz",          "Test knowledge — 25 questions, instant score",  ACCENTS[3]),
]
step_cols = st.columns(6)
for col, (num, title, desc, color) in zip(step_cols, steps):
    with col:
        st.markdown(f"""
        <div class="step-card" style="background:{STEP_BG};border:1px solid {color}18;
                    box-shadow:0 4px 16px {color}0a">
          <div style="width:38px;height:38px;border-radius:11px;margin:0 auto 10px auto;
                      background:{color}12;border:1.5px solid {color}33;display:flex;
                      align-items:center;justify-content:center;font-family:{FONT_CARD};
                      font-size:0.95rem;font-weight:700;color:{color}">
            {num}
          </div>
          <div style="font-size:0.8rem;font-weight:700;color:{TEXT_MAIN};margin-bottom:4px">{title}</div>
          <div style="font-size:0.7rem;color:{TEXT_LO};line-height:1.4">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            font-size:0.73rem;color:{FOOTER_COLOR};font-family:{FONT_CARD}">
  <span>DIP Learning Simulator</span>
  <span>24 pages · 19 tools · {'Dark' if IS_DARK else 'Light'} Theme · Railway MySQL</span>
  <span>Streamlit · OpenCV · ReportLab</span>
</div>""", unsafe_allow_html=True)
