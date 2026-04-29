"""utils/theme_manager.py — Unified Dark/Light theme system with toggle for DIP Simulator v4."""
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# LIGHT THEME
# ─────────────────────────────────────────────────────────────────────────────
LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&family=Poppins:wght@400;600;700;800&display=swap');
:root {
  --bg:         #eaf9fb;
  --surface:    #ffffff;
  --card:       #ffffff;
  --sidebar-bg: #d4f2f6;
  --border:     rgba(85,201,212,0.25);
  --border-hi:  rgba(85,201,212,0.6);
  --accent1:    #55c9d4;
  --accent2:    #88e2eb;
  --accent3:    #4ac5d4;
  --accent4:    #2baebf;
  --accent5:    #40bacc;
  --accent6:    #6bcfdb;
  --text-hi:    #0a2f35;
  --text-mid:   #3d676d;
  --text-lo:    #759fa5;
  --sh-sm:      0 2px 8px rgba(67,97,238,0.08),0 1px 3px rgba(0,0,0,0.05);
  --sh-md:      0 8px 24px rgba(67,97,238,0.12),0 2px 8px rgba(0,0,0,0.06);
  --sh-lg:      0 20px 48px rgba(67,97,238,0.16),0 4px 12px rgba(0,0,0,0.08);
}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg)!important;color:var(--text-hi)!important;}
.stApp{background:radial-gradient(ellipse at 15% 15%,rgba(67,97,238,0.07) 0%,transparent 55%),radial-gradient(ellipse at 85% 85%,rgba(114,9,183,0.06) 0%,transparent 55%),var(--bg)!important;}
section[data-testid="stSidebar"]{background:var(--sidebar-bg)!important;border-right:1px solid var(--border)!important;box-shadow:4px 0 20px rgba(67,97,238,0.07)!important;}
section[data-testid="stSidebar"] *{color:var(--text-hi)!important;}
[data-testid="stMetric"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:16px!important;padding:16px!important;box-shadow:var(--sh-md)!important;transition:all 0.2s!important;}
[data-testid="stMetric"]:hover{transform:translateY(-3px)!important;box-shadow:var(--sh-lg)!important;}
[data-testid="stMetricLabel"]{color:var(--text-mid)!important;font-size:0.72rem!important;letter-spacing:0.1em!important;text-transform:uppercase!important;}
[data-testid="stMetricValue"]{color:var(--accent1)!important;font-family:'JetBrains Mono',monospace!important;font-size:1.4rem!important;}
.stButton button{background:linear-gradient(135deg,var(--accent1),var(--accent2))!important;color:white!important;border:none!important;font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:0.88rem!important;padding:0.6rem 1.6rem!important;border-radius:10px!important;transition:all 0.25s cubic-bezier(0.34,1.56,0.64,1)!important;box-shadow:0 4px 15px rgba(67,97,238,0.32)!important;}
.stButton button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(67,97,238,0.45)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--card)!important;border-radius:12px!important;padding:4px!important;border:1px solid var(--border)!important;box-shadow:var(--sh-sm)!important;}
.stTabs [data-baseweb="tab"]{color:var(--text-mid)!important;font-weight:500!important;border-radius:8px!important;padding:7px 16px!important;transition:all 0.2s!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,var(--accent1),var(--accent2))!important;color:white!important;font-weight:700!important;box-shadow:0 2px 12px rgba(67,97,238,0.35)!important;}
.stSelectbox>div>div{background:var(--card)!important;border:1px solid var(--border)!important;color:var(--text-hi)!important;border-radius:10px!important;box-shadow:var(--sh-sm)!important;}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:var(--card)!important;color:var(--text-hi)!important;border:1px solid var(--border)!important;border-radius:10px!important;}
[data-testid="stFileUploader"]{background:var(--card)!important;border:2px dashed var(--border-hi)!important;border-radius:14px!important;}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;}
h1{font-family:'Poppins',sans-serif!important;color:var(--text-hi)!important;font-weight:800!important;}
h2,h3,h4{font-family:'Poppins',sans-serif!important;color:var(--text-hi)!important;font-weight:700!important;}
hr{border-color:var(--border)!important;}
.stSuccess{background:rgba(6,214,160,0.08)!important;border:1px solid rgba(6,214,160,0.3)!important;border-radius:10px!important;}
.stInfo{background:rgba(76,201,240,0.08)!important;border:1px solid rgba(76,201,240,0.3)!important;border-radius:10px!important;}
.stWarning{background:rgba(248,150,30,0.08)!important;border:1px solid rgba(248,150,30,0.3)!important;border-radius:10px!important;}
.stError{background:rgba(239,35,60,0.08)!important;border:1px solid rgba(239,35,60,0.3)!important;border-radius:10px!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,var(--accent1),var(--accent2));border-radius:4px;}
img{border-radius:10px!important;}
[data-testid="stImage"] img{box-shadow:var(--sh-md)!important;}
.stDeployButton{display:none!important;}#MainMenu{display:none!important;}footer{display:none!important;}
</style>
"""

LIGHT_BG = """
<div style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-2;
  background:radial-gradient(ellipse at 15% 15%,rgba(85,201,212,0.12) 0%,transparent 50%),
  radial-gradient(ellipse at 85% 80%,rgba(136,226,235,0.15) 0%,transparent 50%),
  radial-gradient(ellipse at 60% 10%,rgba(43,174,191,0.08) 0%,transparent 40%),#eaf9fb">
</div>
<div style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;
  background-image:linear-gradient(rgba(85,201,212,0.04) 1px,transparent 1px),
  linear-gradient(90deg,rgba(85,201,212,0.04) 1px,transparent 1px);
  background-size:60px 60px;
  mask-image:linear-gradient(to bottom,transparent,rgba(0,0,0,0.5) 30%,rgba(0,0,0,0.5) 70%,transparent)">
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# DARK THEME (3D Glassmorphism)
# ─────────────────────────────────────────────────────────────────────────────
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Orbitron:wght@400;600;800&family=Poppins:wght@400;600;700;800&display=swap');
:root {
  --bg:         #020818;
  --bg-mid:     #050f28;
  --surface:    #091428;
  --glass:      rgba(10,30,70,0.55);
  --glass-hi:   rgba(20,60,130,0.45);
  --border:     rgba(60,140,255,0.18);
  --border-hi:  rgba(100,180,255,0.35);
  --accent1:    #00a8ff;
  --accent2:    #b44fff;
  --accent3:    #00fff5;
  --accent4:    #00ff9d;
  --accent5:    #ffb700;
  --accent6:    #ff3366;
  --text-hi:    #e8f4ff;
  --text-mid:   #8ab4d4;
  --text-lo:    #3a5a7a;
  --sh-3d:      0 24px 48px rgba(0,0,0,0.6),0 8px 16px rgba(0,168,255,0.08);
  --glow-blue:  0 0 20px rgba(0,168,255,0.4),0 0 40px rgba(0,168,255,0.15);
}
html,body,[class*="css"]{font-family:'Rajdhani',sans-serif!important;background:var(--bg)!important;color:var(--text-hi)!important;}
.stApp{background:radial-gradient(ellipse at 20% 20%,rgba(0,80,200,0.12) 0%,transparent 60%),radial-gradient(ellipse at 80% 80%,rgba(100,0,200,0.10) 0%,transparent 60%),var(--bg)!important;min-height:100vh!important;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(5,20,55,0.98),rgba(2,8,24,0.98))!important;border-right:1px solid var(--border)!important;box-shadow:4px 0 32px rgba(0,0,0,0.5)!important;}
section[data-testid="stSidebar"] *{color:var(--text-hi)!important;}
[data-testid="stMetric"]{background:var(--glass)!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:14px 16px!important;box-shadow:var(--sh-3d),inset 0 1px 0 rgba(255,255,255,0.06)!important;backdrop-filter:blur(12px)!important;transform:perspective(600px) rotateX(2deg)!important;transition:all 0.2s!important;}
[data-testid="stMetric"]:hover{transform:perspective(600px) rotateX(0deg) translateY(-2px)!important;box-shadow:var(--sh-3d),var(--glow-blue)!important;}
[data-testid="stMetricLabel"]{color:var(--text-mid)!important;font-size:0.72rem!important;letter-spacing:0.1em!important;text-transform:uppercase!important;}
[data-testid="stMetricValue"]{color:var(--accent3)!important;font-family:'JetBrains Mono',monospace!important;font-size:1.3rem!important;text-shadow:0 0 10px rgba(0,255,245,0.5)!important;}
.stButton button{background:linear-gradient(135deg,rgba(0,80,200,0.8),rgba(80,0,200,0.8))!important;color:white!important;border:1px solid var(--border-hi)!important;font-family:'Rajdhani',sans-serif!important;font-weight:600!important;font-size:0.88rem!important;letter-spacing:0.06em!important;padding:0.55rem 1.6rem!important;border-radius:8px!important;transition:all 0.25s!important;box-shadow:0 4px 15px rgba(0,80,200,0.4)!important;transform:perspective(400px) translateZ(0)!important;}
.stButton button:hover{transform:perspective(400px) translateZ(8px) translateY(-2px)!important;box-shadow:0 8px 25px rgba(0,80,200,0.55),var(--glow-blue)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--glass)!important;border-radius:12px!important;padding:4px!important;border:1px solid var(--border)!important;backdrop-filter:blur(8px)!important;}
.stTabs [data-baseweb="tab"]{color:var(--text-mid)!important;font-weight:600!important;border-radius:8px!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(0,100,255,0.7),rgba(80,0,200,0.7))!important;color:white!important;font-weight:700!important;box-shadow:0 2px 12px rgba(0,100,255,0.4)!important;text-shadow:0 0 8px rgba(0,200,255,0.6)!important;}
.stSelectbox>div>div{background:var(--glass)!important;border:1px solid var(--border)!important;color:var(--text-hi)!important;border-radius:8px!important;backdrop-filter:blur(8px)!important;}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:var(--glass)!important;color:var(--text-hi)!important;border:1px solid var(--border)!important;border-radius:8px!important;backdrop-filter:blur(8px)!important;}
[data-testid="stFileUploader"]{background:var(--glass)!important;border:1.5px dashed var(--border-hi)!important;border-radius:12px!important;backdrop-filter:blur(8px)!important;}
[data-testid="stExpander"]{background:var(--glass)!important;border:1px solid var(--border)!important;border-radius:12px!important;backdrop-filter:blur(8px)!important;}
h1{font-family:'Orbitron',monospace!important;color:var(--text-hi)!important;}
h2,h3,h4{font-family:'Rajdhani',sans-serif!important;color:var(--text-hi)!important;font-weight:600!important;}
hr{border-color:var(--border)!important;}
.stSuccess{background:rgba(0,200,120,0.1)!important;border:1px solid rgba(0,200,120,0.3)!important;border-radius:8px!important;}
.stInfo{background:rgba(0,140,255,0.1)!important;border:1px solid rgba(0,140,255,0.3)!important;border-radius:8px!important;}
.stWarning{background:rgba(255,180,0,0.1)!important;border:1px solid rgba(255,180,0,0.3)!important;border-radius:8px!important;}
.stError{background:rgba(255,50,80,0.1)!important;border:1px solid rgba(255,50,80,0.3)!important;border-radius:8px!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,var(--accent1),var(--accent2));border-radius:4px;}
img{border-radius:8px!important;}
[data-testid="stImage"] img{box-shadow:0 8px 24px rgba(0,0,0,0.4),0 0 1px var(--border-hi)!important;}
.stDeployButton{display:none!important;}#MainMenu{display:none!important;}footer{display:none!important;}
</style>
"""

DARK_BG = """
<div id="particles-bg" style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;overflow:hidden"></div>
<style>
@keyframes float-up{0%{transform:translateY(100vh) scale(0);opacity:0}10%{opacity:0.6}90%{opacity:0.3}100%{transform:translateY(-10vh) translateX(var(--drift)) scale(1);opacity:0}}
.dip-particle{position:absolute;bottom:-10px;width:var(--sz);height:var(--sz);border-radius:50%;background:var(--clr);box-shadow:0 0 6px var(--clr),0 0 12px var(--clr);animation:float-up var(--dur) var(--delay) infinite ease-in}
</style>
<script>
(function(){var bg=document.getElementById('particles-bg');if(!bg)return;
var c=['#00a8ff','#00fff5','#b44fff','#00ff9d','#ffb700'];
for(var i=0;i<24;i++){var p=document.createElement('div');p.className='dip-particle';
var sz=(Math.random()*3+1).toFixed(1)+'px';var dur=(Math.random()*12+8).toFixed(1)+'s';
var delay=(Math.random()*15).toFixed(1)+'s';var left=(Math.random()*100).toFixed(1)+'%';
var drift=((Math.random()-0.5)*80).toFixed(0)+'px';var clr=c[Math.floor(Math.random()*c.length)];
p.style.cssText='--sz:'+sz+';--dur:'+dur+';--delay:'+delay+';--drift:'+drift+';--clr:'+clr+';left:'+left;
bg.appendChild(p);}})();
</script>
<div style="position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;
  background-image:linear-gradient(rgba(0,100,255,0.04) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,100,255,0.04) 1px,transparent 1px);
  background-size:60px 60px;
  mask-image:linear-gradient(to bottom,transparent,rgba(0,0,0,0.3) 30%,rgba(0,0,0,0.3) 70%,transparent)">
</div>
"""

# ─────────────────────────────────────────────────────────────────────────────
# THEME TOGGLE WIDGET (fixed floating button)
# ─────────────────────────────────────────────────────────────────────────────
TOGGLE_CSS = """
<style>
#theme-toggle-btn {
  position: fixed;
  top: 14px;
  right: 80px;
  z-index: 9999;
  background: linear-gradient(135deg, #4361ee, #7209b7);
  border: none;
  border-radius: 50px;
  padding: 8px 18px;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(67,97,238,0.4);
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  color: white;
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  letter-spacing: 0.03em;
  white-space: nowrap;
}
#theme-toggle-btn:hover {
  transform: scale(1.08) translateY(-2px);
  box-shadow: 0 8px 30px rgba(67,97,238,0.55);
}
#theme-toggle-btn:active { transform: scale(0.97); }
</style>
"""

def get_theme() -> str:
    """Return current theme from session state."""
    return st.session_state.get("theme", "light")


def inject_theme():
    """Inject current theme CSS + background into the page."""
    theme = get_theme()
    if theme == "dark":
        st.markdown(DARK_CSS, unsafe_allow_html=True)
        st.markdown(DARK_BG, unsafe_allow_html=True)
    else:
        st.markdown(LIGHT_CSS, unsafe_allow_html=True)
        st.markdown(LIGHT_BG, unsafe_allow_html=True)


def theme_toggle_button():
    """Render the floating theme toggle button in the sidebar."""
    theme = get_theme()
    icon  = "☀️" if theme == "dark" else "🌙"
    label = "Light Mode" if theme == "dark" else "Dark Mode"

    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        st.markdown(f"<div style='font-size:1.5rem;padding-top:4px'>{icon}</div>",
                    unsafe_allow_html=True)
    with col2:
        if st.sidebar.button(f"{label}", key="theme_toggle_btn", use_container_width=True):
            new_theme = "light" if theme == "dark" else "dark"
            st.session_state["theme"] = new_theme
            # Try to save to DB
            user = st.session_state.get("current_user")
            if user:
                try:
                    from utils.db import save_theme
                    save_theme(user, new_theme)
                except Exception:
                    pass
            st.rerun()


# Backward compat aliases used by old pages
LIGHT_THEME_CSS    = LIGHT_CSS
LIGHT_BG_PATTERNS  = LIGHT_BG
