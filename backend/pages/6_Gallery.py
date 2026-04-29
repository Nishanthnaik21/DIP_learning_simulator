import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from utils.helpers import *



st.set_page_config(page_title="Sample Gallery", page_icon="🖼️", layout="wide")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj

st.markdown("## 🖼️ Sample Image Gallery")
st.caption("10 classic DIP test images — pick the right one for each module")
st.markdown("---")

SAMPLES_DIR_ABS = os.path.join(os.path.dirname(__file__), "..", "assets", "samples")

# Check samples exist
if not os.path.exists(SAMPLES_DIR_ABS) or not os.listdir(SAMPLES_DIR_ABS):
    st.warning("⚠️ Sample images not generated yet.")
    if st.button("🔧 Generate all sample images now"):
        import subprocess, sys
        script = os.path.join(os.path.dirname(__file__), "..", "assets", "generate_samples.py")
        subprocess.run([sys.executable, script])
        st.success("Done! Reload the page."); st.rerun()
    st.stop()

st.markdown("""
<div style="background:#f0f4ff;border-left:4px solid #4f6ef7;border-radius:0 8px 8px 0;
padding:12px 16px;margin-bottom:20px;font-size:0.88rem;color:#2d3a6b">
📖 All 10 images are <b>generated programmatically</b> — no downloads needed. Each is designed 
to demonstrate specific DIP operations clearly. Use the <b>sidebar gallery picker</b> on any module 
page to select one as input.
</div>""", unsafe_allow_html=True)

# Module filter
module_filter = st.selectbox("Filter by best module", 
    ["All modules","M1 — Fundamentals","M2 — Spatial/Freq","M3 — Restoration",
     "M4 — Color/Morphology","M5 — Segmentation"])

# ── Gallery grid ───────────────────────────────────────────────────────────────
files = sorted(SAMPLE_META.keys())
n_cols = 3
cols = st.columns(n_cols)

shown = 0
for fname, meta in SAMPLE_META.items():
    # Apply filter
    if module_filter != "All modules":
        short_mod = module_filter.split("—")[0].strip()  # "M2"
        if short_mod not in meta["best_for"]:
            continue

    path = os.path.join(SAMPLES_DIR_ABS, fname)
    if not os.path.exists(path):
        continue

    img = cv2.imread(path)
    if img is None: continue
    if len(img.shape) == 3:
        img_show = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img_show = img

    with cols[shown % n_cols]:
        st.image(img_show, caption=meta["name"], use_container_width=True)
        st.markdown(f"""
        <div style="background:#f8f9ff;border:1px solid #e0e7ff;border-radius:8px;
                    padding:10px 12px;margin-bottom:16px;font-size:0.8rem">
          <div style="font-weight:600;color:#3730a3;margin-bottom:4px">{meta['name']}</div>
          <div style="color:#6366f1;margin-bottom:4px">✅ Best for: {meta['best_for']}</div>
          <div style="color:#6b7280">{meta['desc']}</div>
          <div style="margin-top:6px;color:#9ca3af;font-size:0.75rem">
            Size: {img_show.shape[1]}×{img_show.shape[0]} · 
            {'Grayscale' if len(img_show.shape)==2 or (len(img_show.shape)==3 and img_show[:,:,0].tolist()==img_show[:,:,1].tolist()) else 'RGB'}
          </div>
        </div>""", unsafe_allow_html=True)
    shown += 1

if shown == 0:
    st.info("No images match the selected filter.")

st.markdown("---")

# ── Detailed view ──────────────────────────────────────────────────────────────
st.markdown("### 🔍 Detailed Image Analysis")
selected = st.selectbox("Select an image for detailed analysis",
                         list(SAMPLE_META.keys()),
                         format_func=lambda x: SAMPLE_META[x]["name"])

path = os.path.join(SAMPLES_DIR_ABS, selected)
img  = cv2.imread(path)
if img is not None:
    if len(img.shape) == 3:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_rgb = img; gray = img

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Original**")
        st.image(img_rgb, use_container_width=True)
    with c2:
        st.markdown("**Greyscale**")
        st.image(gray, use_container_width=True)
    with c3:
        st.markdown("**Histogram**")
        fig, ax = plt.subplots(figsize=(4,3))
        hist = cv2.calcHist([gray],[0],None,[256],[0,256]).flatten()
        ax.bar(range(256), hist, color="#4f6ef7", width=1, alpha=0.85)
        ax.set_xlabel("Intensity"); ax.set_ylabel("Frequency")
        ax.set_title("Greyscale histogram")
        plt.tight_layout()
        buf = __import__("io").BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches="tight"); buf.seek(0)
        st.image(buf, use_container_width=True)
        plt.close(fig)

    meta = SAMPLE_META[selected]
    st.markdown(f"""
    <div style="background:#f0f4ff;border-left:4px solid #4f6ef7;border-radius:0 8px 8px 0;
                padding:12px 16px;margin-top:12px;font-size:0.85rem;color:#2d3a6b">
    <b>Why this image is recommended:</b> {meta['desc']}<br><br>
    <b>Best used in:</b> {meta['best_for']}<br>
    <b>Image size:</b> {img_rgb.shape[1]}×{img_rgb.shape[0]} pixels<br>
    <b>Mean intensity:</b> {gray.mean():.1f} &nbsp;&nbsp; <b>Std:</b> {gray.std():.1f} &nbsp;&nbsp;
    <b>Min:</b> {gray.min()} &nbsp;&nbsp; <b>Max:</b> {gray.max()}
    </div>""", unsafe_allow_html=True)

    # Store for session use
    st.session_state["gallery_selection"] = img_rgb
    st.success("✅ This image is now available as 'Lena (synthetic)' etc. in the sidebar gallery picker on any module page.")
