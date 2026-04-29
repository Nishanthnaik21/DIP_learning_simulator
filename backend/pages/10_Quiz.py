import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import matplotlib.pyplot as plt
import io
from utils.helpers import *



st.set_page_config(page_title="DIP Quiz", page_icon="🧠", layout="wide")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj

st.markdown("## 🧠 DIP Knowledge Quiz")
st.caption("Test your understanding of all 5 modules — 5 MCQs per module · Instant feedback · Detailed explanations")
st.markdown("---")

# ── Module selection ───────────────────────────────────────────────────────────
modules_list = list(QUIZ_BANK.keys())

col1, col2 = st.columns([2, 1])
with col1:
    selected_module = st.selectbox("Select module to test", modules_list)
with col2:
    mode = st.radio("Mode", ["Single module","Take all modules"], horizontal=True)

st.markdown("---")

# ── Scoreboard ─────────────────────────────────────────────────────────────────
if "quiz_history" not in st.session_state:
    st.session_state["quiz_history"] = {}

if st.session_state["quiz_history"]:
    st.markdown("#### 📊 Your Progress")
    score_cols = st.columns(len(st.session_state["quiz_history"]))
    for col, (mod, score) in zip(score_cols, st.session_state["quiz_history"].items()):
        total = len(QUIZ_BANK.get(mod, []))
        pct   = (score/total*100) if total else 0
        colour = "normal" if pct < 40 else "off" if pct < 70 else "normal"
        short = mod.split("—")[0].strip()
        col.metric(short, f"{score}/{total}", f"{pct:.0f}%")

    # Progress chart
    if len(st.session_state["quiz_history"]) > 1:
        fig, ax = plt.subplots(figsize=(8, 2.5))
        mods  = [m.split("—")[0].strip() for m in st.session_state["quiz_history"]]
        pcts  = [(v/len(QUIZ_BANK.get(k,[])) * 100)
                  for k,v in st.session_state["quiz_history"].items()]
        colours = ["#22c55e" if p>=70 else "#f59e0b" if p>=40 else "#ef4444" for p in pcts]
        ax.bar(mods, pcts, color=colours, alpha=0.85, edgecolor="white", linewidth=0.5)
        ax.axhline(70, color="#22c55e", linestyle="--", alpha=0.5, label="Pass (70%)")
        ax.set_ylabel("Score %"); ax.set_ylim(0,105); ax.legend(fontsize=8)
        ax.set_title("Quiz Performance by Module", fontsize=10)
        plt.tight_layout()
        buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0); st.image(buf, use_container_width=False, width=640)
        plt.close(fig)

    if st.button("🔄 Reset all scores"):
        st.session_state["quiz_history"] = {}
        # Clear all quiz states
        for k in list(st.session_state.keys()):
            if k.startswith("mod_quiz_"):
                del st.session_state[k]
        st.rerun()

    st.markdown("---")

# ── Quiz rendering ─────────────────────────────────────────────────────────────
if mode == "Single module":
    st.markdown(f"### 📝 {selected_module}")
    prefix = f"mod_quiz_{selected_module.replace(' ','_')[:20]}"
    result = render_quiz(selected_module, prefix)
    if result is not None:
        st.session_state["quiz_history"][selected_module] = result

else:
    # All modules — accordion style
    st.markdown("### 📝 Full Assessment — All Modules")
    st.info("Complete each module quiz below. Your scores are tracked in the progress panel above.")

    for mod in modules_list:
        with st.expander(f"📖 {mod}", expanded=False):
            prefix = f"mod_quiz_{mod.replace(' ','_')[:20]}"
            result = render_quiz(mod, prefix)
            if result is not None:
                st.session_state["quiz_history"][mod] = result

# ── Quick reference card ───────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Quick Formula Reference Card"):
    st.markdown("""
    | Concept | Formula | Key points |
    |---------|---------|------------|
    | Grey levels | 2^N | 8-bit = 256 levels |
    | Image negative | I_out = 255 − I_in | Inverts brightness |
    | Gamma correction | I_out = I_in^γ | γ<1 brightens, γ>1 darkens |
    | Log transform | I_out = c·log(1+I_in) | Compresses high values |
    | PSNR | 20·log10(255/√MSE) | Higher = better quality |
    | Gaussian kernel | G(x,y) = e^(−(x²+y²)/2σ²) | σ controls blur radius |
    | DFT magnitude | log(1 + |F(u,v)|) | Centre = DC (low freq) |
    | Wiener filter | H* / (|H|² + K) | K = noise/signal ratio |
    | Harris response | R = det(M) − k·trace(M)² | R>0: corner, R<0: edge |
    | Hu moments | h1–h7 | Invariant: rotation, scale, translation |
    | Damage % | union_pixels / total_pixels × 100 | — |
    | Circularity | 4πA / P² | Circle=1.0, Square≈0.785 |
    | Otsu threshold | min(σ²_within) | = max(σ²_between) |
    | Morphological gradient | Dilation − Erosion | Extracts boundaries |
    """)
