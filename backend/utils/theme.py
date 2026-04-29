"""utils/theme.py — 3D Glassmorphism UI theme system."""

# ─────────────────────────────────────────────────────────────────────────────
# Complete 3D CSS — glassmorphism, depth layers, 3D card flips, particle bg
# ─────────────────────────────────────────────────────────────────────────────
THEME_3D = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Orbitron:wght@400;600;800&display=swap');

:root {
  --bg-deep:    #020818;
  --bg-mid:     #050f28;
  --bg-surface: #091428;
  --glass:      rgba(10, 30, 70, 0.55);
  --glass-hi:   rgba(20, 60, 130, 0.45);
  --glass-brd:  rgba(60, 140, 255, 0.18);
  --glass-brd2: rgba(100, 180, 255, 0.35);
  --neon-blue:  #00a8ff;
  --neon-cyan:  #00fff5;
  --neon-purple:#b44fff;
  --neon-green: #00ff9d;
  --neon-amber: #ffb700;
  --neon-red:   #ff3366;
  --text-hi:    #e8f4ff;
  --text-mid:   #8ab4d4;
  --text-lo:    #3a5a7a;
  --shadow-3d:  0 24px 48px rgba(0,0,0,0.6), 0 8px 16px rgba(0,168,255,0.08);
  --glow-blue:  0 0 20px rgba(0,168,255,0.4), 0 0 40px rgba(0,168,255,0.15);
  --glow-cyan:  0 0 20px rgba(0,255,245,0.4), 0 0 40px rgba(0,255,245,0.15);
  --glow-purple:0 0 20px rgba(180,79,255,0.4),0 0 40px rgba(180,79,255,0.15);
}

/* ── GLOBAL RESET ── */
html, body, [class*="css"] {
  font-family: 'Rajdhani', sans-serif !important;
  background: var(--bg-deep) !important;
  color: var(--text-hi) !important;
  -webkit-font-smoothing: antialiased;
}

.stApp {
  background:
    radial-gradient(ellipse at 20% 20%, rgba(0,80,200,0.12) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 80%, rgba(100,0,200,0.10) 0%, transparent 60%),
    radial-gradient(ellipse at 50% 50%, rgba(0,40,100,0.08) 0%, transparent 80%),
    var(--bg-deep) !important;
  min-height: 100vh !important;
}

/* ── SIDEBAR 3D PANEL ── */
section[data-testid="stSidebar"] {
  background:
    linear-gradient(180deg, rgba(5,20,55,0.98) 0%, rgba(2,8,24,0.98) 100%) !important;
  border-right: 1px solid var(--glass-brd) !important;
  box-shadow: 4px 0 32px rgba(0,0,0,0.5), inset -1px 0 0 rgba(60,140,255,0.08) !important;
}
section[data-testid="stSidebar"] * { color: var(--text-hi) !important; }
section[data-testid="stSidebar"] .stSelectbox > label,
section[data-testid="stSidebar"] .stSlider > label {
  color: var(--text-mid) !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.05em !important;
}

/* ── GLASS METRICS ── */
[data-testid="stMetric"] {
  background: var(--glass) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 12px !important;
  padding: 14px 16px !important;
  box-shadow: var(--shadow-3d), inset 0 1px 0 rgba(255,255,255,0.06) !important;
  backdrop-filter: blur(12px) !important;
  transform: perspective(600px) rotateX(2deg) !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
  position: relative !important;
  overflow: hidden !important;
}
[data-testid="stMetric"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,168,255,0.6), transparent);
}
[data-testid="stMetric"]:hover {
  transform: perspective(600px) rotateX(0deg) translateY(-2px) !important;
  box-shadow: var(--shadow-3d), var(--glow-blue) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-mid) !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  color: var(--neon-cyan) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.3rem !important;
  text-shadow: 0 0 10px rgba(0,255,245,0.5) !important;
}

/* ── 3D BUTTONS ── */
.stButton button {
  background: linear-gradient(135deg, rgba(0,80,200,0.8), rgba(80,0,200,0.8)) !important;
  color: white !important;
  border: 1px solid var(--glass-brd2) !important;
  font-family: 'Rajdhani', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.06em !important;
  padding: 0.55rem 1.6rem !important;
  border-radius: 8px !important;
  transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
  box-shadow: 0 4px 15px rgba(0,80,200,0.4), 0 1px 3px rgba(0,0,0,0.3),
              inset 0 1px 0 rgba(255,255,255,0.15) !important;
  transform: perspective(400px) translateZ(0) !important;
  position: relative !important;
  overflow: hidden !important;
}
.stButton button::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.4s;
}
.stButton button:hover {
  transform: perspective(400px) translateZ(8px) translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(0,80,200,0.55), var(--glow-blue) !important;
}
.stButton button:hover::before { left: 100%; }
.stButton button:active {
  transform: perspective(400px) translateZ(-2px) translateY(1px) !important;
}
.stDownloadButton button {
  background: linear-gradient(135deg, rgba(0,150,100,0.8), rgba(0,80,200,0.8)) !important;
  box-shadow: 0 4px 15px rgba(0,150,100,0.4), inset 0 1px 0 rgba(255,255,255,0.1) !important;
}

/* ── 3D TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--glass) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  border: 1px solid var(--glass-brd) !important;
  box-shadow: inset 0 2px 8px rgba(0,0,0,0.3), 0 1px 0 rgba(255,255,255,0.04) !important;
  backdrop-filter: blur(8px) !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--text-mid) !important;
  font-weight: 600 !important;
  font-size: 0.8rem !important;
  letter-spacing: 0.06em !important;
  border-radius: 8px !important;
  padding: 7px 16px !important;
  transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(0,100,255,0.7), rgba(80,0,200,0.7)) !important;
  color: white !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 12px rgba(0,100,255,0.4), inset 0 1px 0 rgba(255,255,255,0.15) !important;
  text-shadow: 0 0 8px rgba(0,200,255,0.6) !important;
}

/* ── GLASS SLIDERS ── */
.stSlider > div > div > div { background: rgba(0,80,200,0.25) !important; border-radius: 4px !important; }
.stSlider > div > div > div > div {
  background: linear-gradient(90deg, var(--neon-blue), var(--neon-cyan)) !important;
  box-shadow: 0 0 8px rgba(0,168,255,0.6) !important;
}

/* ── GLASS SELECT BOXES ── */
.stSelectbox > div > div {
  background: var(--glass) !important;
  border: 1px solid var(--glass-brd) !important;
  color: var(--text-hi) !important;
  border-radius: 8px !important;
  backdrop-filter: blur(8px) !important;
}

/* ── GLASS FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  background: var(--glass) !important;
  border: 1.5px dashed var(--glass-brd2) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(8px) !important;
  box-shadow: inset 0 2px 12px rgba(0,0,0,0.2) !important;
}

/* ── GLASS EXPANDERS ── */
[data-testid="stExpander"] {
  background: var(--glass) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(8px) !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div {
  background: rgba(0,40,100,0.4) !important;
  border-radius: 6px !important;
  border: 1px solid var(--glass-brd) !important;
}
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--neon-blue), var(--neon-cyan), var(--neon-purple)) !important;
  box-shadow: 0 0 10px rgba(0,168,255,0.5) !important;
  border-radius: 6px !important;
}

/* ── HEADINGS ── */
h1 { font-family: 'Orbitron', monospace !important; color: var(--text-hi) !important; }
h2, h3, h4 { font-family: 'Rajdhani', sans-serif !important; color: var(--text-hi) !important; font-weight: 600 !important; }
hr { border-color: var(--glass-brd) !important; }
.stCaption { color: var(--text-lo) !important; }

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
  background: var(--glass) !important;
  color: var(--text-hi) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 8px !important;
  backdrop-filter: blur(8px) !important;
}

/* ── FORMS ── */
[data-testid="stForm"] {
  background: var(--glass) !important;
  border: 1px solid var(--glass-brd) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(12px) !important;
  box-shadow: 0 16px 40px rgba(0,0,0,0.4) !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
  background: var(--glass) !important;
  border-radius: 10px !important;
  border: 1px solid var(--glass-brd) !important;
}

/* ── ALERTS ── */
.stSuccess { background: rgba(0,200,120,0.1) !important; border: 1px solid rgba(0,200,120,0.3) !important; border-radius: 8px !important; }
.stInfo    { background: rgba(0,140,255,0.1) !important; border: 1px solid rgba(0,140,255,0.3) !important; border-radius: 8px !important; }
.stWarning { background: rgba(255,180,0,0.1)  !important; border: 1px solid rgba(255,180,0,0.3)  !important; border-radius: 8px !important; }
.stError   { background: rgba(255,50,80,0.1)  !important; border: 1px solid rgba(255,50,80,0.3)  !important; border-radius: 8px !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--neon-blue), var(--neon-purple)); border-radius: 4px; }

/* ── RADIO / CHECKBOX ── */
.stRadio label, .stCheckbox label { color: var(--text-hi) !important; }

/* ── IMAGE BORDERS ── */
img { border-radius: 8px !important; }
[data-testid="stImage"] img {
  box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 0 1px var(--glass-brd2) !important;
}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# PARTICLE BACKGROUND (pure CSS/JS, no canvas needed)
# ─────────────────────────────────────────────────────────────────────────────
PARTICLES_HTML = """
<div id="particles-bg" style="position:fixed;top:0;left:0;width:100%;height:100%;
     pointer-events:none;z-index:-1;overflow:hidden">
</div>
<style>
@keyframes float-up {
  0%   { transform: translateY(100vh) translateX(0) scale(0); opacity:0; }
  10%  { opacity: 0.6; }
  90%  { opacity: 0.3; }
  100% { transform: translateY(-10vh) translateX(var(--drift)) scale(1); opacity:0; }
}
.particle {
  position: absolute;
  bottom: -10px;
  width: var(--sz);
  height: var(--sz);
  border-radius: 50%;
  background: var(--clr);
  box-shadow: 0 0 6px var(--clr), 0 0 12px var(--clr);
  animation: float-up var(--dur) var(--delay) infinite ease-in;
}
</style>
<script>
(function(){
  var bg = document.getElementById('particles-bg');
  if(!bg) return;
  var colours = ['#00a8ff','#00fff5','#b44fff','#00ff9d','#ffb700'];
  for(var i=0;i<28;i++){
    var p = document.createElement('div');
    p.className = 'particle';
    var sz = (Math.random()*3+1).toFixed(1)+'px';
    var dur = (Math.random()*12+8).toFixed(1)+'s';
    var delay= (Math.random()*15).toFixed(1)+'s';
    var left = (Math.random()*100).toFixed(1)+'%';
    var drift= ((Math.random()-0.5)*80).toFixed(0)+'px';
    var clr  = colours[Math.floor(Math.random()*colours.length)];
    p.style.cssText = '--sz:'+sz+';--dur:'+dur+';--delay:'+delay+
                      ';--drift:'+drift+';--clr:'+clr+';left:'+left;
    bg.appendChild(p);
  }
})();
</script>
"""

# ─────────────────────────────────────────────────────────────────────────────
# GRID LINES OVERLAY (subtle perspective grid)
# ─────────────────────────────────────────────────────────────────────────────
GRID_HTML = """
<div style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;
     background-image:linear-gradient(rgba(0,100,255,0.04) 1px,transparent 1px),
     linear-gradient(90deg,rgba(0,100,255,0.04) 1px,transparent 1px);
     background-size:60px 60px;mask-image:linear-gradient(to bottom,transparent 0%,rgba(0,0,0,0.3) 30%,rgba(0,0,0,0.3) 70%,transparent 100%)">
</div>
"""

def inject(title="DIP Simulator v4", icon="🔬", show_particles=True):
    import streamlit as st
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    st.markdown(THEME_3D, unsafe_allow_html=True)
    if show_particles:
        st.markdown(PARTICLES_HTML + GRID_HTML, unsafe_allow_html=True)

def page_header(title, subtitle, icon, color="#00a8ff"):
    import streamlit as st
    st.markdown(f"""
    <div style="padding:20px 0 16px 0;margin-bottom:20px;position:relative">
      <div style="position:absolute;bottom:0;left:0;right:0;height:1px;
                  background:linear-gradient(90deg,transparent,{color}88,transparent)"></div>
      <div style="display:flex;align-items:center;gap:16px">
        <div style="width:48px;height:48px;
                    background:linear-gradient(135deg,{color}22,{color}44);
                    border:1.5px solid {color}66;border-radius:12px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.4rem;box-shadow:0 0 20px {color}33,
                    inset 0 1px 0 rgba(255,255,255,0.1);
                    transform:perspective(400px) rotateY(-5deg)">{icon}</div>
        <div>
          <div style="font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:700;
                      color:{color};letter-spacing:0.05em;
                      text-shadow:0 0 20px {color}66">{title}</div>
          <div style="font-size:0.72rem;color:var(--text-mid);letter-spacing:0.15em;
                      margin-top:2px;text-transform:uppercase">{subtitle}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

def glass_card(content_html, color="#00a8ff", glow=False):
    import streamlit as st
    glow_css = f"box-shadow:var(--shadow-3d),0 0 30px {color}22;" if glow else "box-shadow:var(--shadow-3d);"
    st.markdown(f"""
    <div style="background:var(--glass);border:1px solid {color}33;border-radius:14px;
                padding:18px 20px;margin:10px 0;
                backdrop-filter:blur(12px);
                {glow_css}
                transform:perspective(800px) rotateX(1deg);
                position:relative;overflow:hidden">
      <div style="position:absolute;top:0;left:0;right:0;height:1px;
                  background:linear-gradient(90deg,transparent,{color}66,transparent)"></div>
      {content_html}
    </div>""", unsafe_allow_html=True)

def theory_card(text, title="Theory"):
    import streamlit as st
    st.markdown(f"""
    <div style="background:rgba(0,60,140,0.3);border:1px solid rgba(0,168,255,0.25);
                border-left:3px solid var(--neon-blue);border-radius:0 10px 10px 0;
                padding:12px 16px;margin:10px 0;font-size:0.84rem;
                color:#a8d4f8;line-height:1.7;
                box-shadow:inset 0 0 20px rgba(0,80,200,0.1)">
      <span style="font-weight:700;color:var(--neon-blue);font-family:'Orbitron',monospace;
                   font-size:0.72rem;letter-spacing:0.1em">📖 {title.upper()}: </span>{text}
    </div>""", unsafe_allow_html=True)

def code_card(code):
    import streamlit as st
    st.markdown(f"""
    <div style="background:rgba(0,5,15,0.85);border:1px solid rgba(0,168,255,0.2);
                border-radius:10px;padding:16px;margin:10px 0;
                font-family:'JetBrains Mono',monospace;font-size:0.77rem;
                color:#7dd3fc;white-space:pre;overflow-x:auto;line-height:1.7;
                box-shadow:inset 0 0 30px rgba(0,0,0,0.5)">
{code}
    </div>""", unsafe_allow_html=True)

def neon_metric(label, value, color="#00a8ff", sub=None):
    import streamlit as st
    sub_html = f'<div style="font-size:0.68rem;color:var(--text-lo);margin-top:2px">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div style="background:var(--glass);border:1px solid {color}33;border-radius:10px;
                padding:14px 16px;text-align:center;
                box-shadow:var(--shadow-3d),0 0 15px {color}11;
                transform:perspective(500px) rotateX(2deg);
                position:relative;overflow:hidden">
      <div style="position:absolute;top:0;left:0;right:0;height:1px;
                  background:linear-gradient(90deg,transparent,{color}88,transparent)"></div>
      <div style="font-size:0.68rem;color:var(--text-mid);letter-spacing:0.1em;
                  text-transform:uppercase;margin-bottom:6px">{label}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.3rem;font-weight:600;
                  color:{color};text-shadow:0 0 12px {color}88">{value}</div>
      {sub_html}
    </div>""", unsafe_allow_html=True)

def section_title(text, color="#00a8ff"):
    import streamlit as st
    st.markdown(f"""
    <div style="margin:20px 0 12px 0;display:flex;align-items:center;gap:12px">
      <div style="width:3px;height:20px;background:linear-gradient(180deg,{color},{color}44);
                  border-radius:2px;box-shadow:0 0 8px {color}88"></div>
      <div style="font-family:'Orbitron',monospace;font-size:0.78rem;font-weight:600;
                  color:{color};letter-spacing:0.15em;text-transform:uppercase;
                  text-shadow:0 0 12px {color}44">{text}</div>
    </div>""", unsafe_allow_html=True)

def metric_row(items, colors=None):
    import streamlit as st
    default_colors = ["#00a8ff","#00fff5","#b44fff","#00ff9d","#ffb700","#ff3366"]
    cols = st.columns(len(items))
    for i, (col, (label, val)) in enumerate(zip(cols, items)):
        clr = (colors[i] if colors and i < len(colors) else default_colors[i % len(default_colors)])
        with col:
            neon_metric(label, val, clr)

def psnr(original, noisy):
    import numpy as np
    mse = np.mean((original.astype(float) - noisy.astype(float))**2)
    if mse == 0: return 100.0
    return 20 * np.log10(255.0 / np.sqrt(mse))
