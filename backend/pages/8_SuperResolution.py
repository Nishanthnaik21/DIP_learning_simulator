import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from utils.helpers import *



st.set_page_config(page_title="Super Resolution", page_icon="🔭", layout="wide")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj

st.markdown("## 🔭 Super Resolution")
st.caption("Upscale low-resolution images using classical interpolation + sharpening. Compare 6 methods side by side.")
st.markdown("---")

img_rgb = upload_image("sr_upload")
gray    = to_gray(img_rgb)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔭 SR Settings")
scale = st.sidebar.select_slider("Upscale factor", [2, 3, 4], 2)

theory_box(
    "Super Resolution reconstructs a higher-resolution image from a lower-resolution input. "
    "Classical methods use interpolation: Nearest (blocky), Bilinear (smooth, slightly blurry), "
    "Bicubic (sharper — used in Photoshop), Lanczos (sharpest classical method). "
    "Post-processing sharpening via unsharp masking or Laplacian edge boost can further improve perceived quality. "
    "ML-based SR (ESRGAN, Real-ESRGAN) would be added here in a production system."
)

# ── Simulate low-res input ─────────────────────────────────────────────────────
st.markdown("### Step 1: Simulate Low-Resolution Input")
downsample_factor = st.slider("Downsample factor (simulate low-res camera)", 2, 8, 4)
h, w = gray.shape
lr_h, lr_w = max(1, h//downsample_factor), max(1, w//downsample_factor)
lr_img = cv2.resize(gray, (lr_w, lr_h), interpolation=cv2.INTER_AREA)

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**High-res original ({w}×{h})**")
    st.image(gray, use_container_width=True, clamp=True)
with c2:
    st.markdown(f"**Low-res input ({lr_w}×{lr_h}) — ×{downsample_factor} downsampled**")
    st.image(lr_img, use_container_width=True, clamp=True)

metric_row([
    ("Original", f"{w}×{h}"),
    ("Low-res",  f"{lr_w}×{lr_h}"),
    ("SR target",f"{lr_w*scale}×{lr_h*scale}"),
    ("Scale",    f"×{scale}"),
])

st.markdown("---")

# ── Run all methods ────────────────────────────────────────────────────────────
st.markdown("### Step 2: Upscale Comparison — All 6 Methods")

methods = ["Nearest","Bilinear","Bicubic","Lanczos","Lanczos + Sharpen","Lanczos + Edge-Boost"]
results = {}
for m in methods:
    results[m] = super_resolve(lr_img, scale, m)

cols_sr = st.columns(3)
for i, m in enumerate(methods):
    with cols_sr[i % 3]:
        sr_u8 = results[m]
        p = psnr(cv2.resize(gray, (sr_u8.shape[1], sr_u8.shape[0]), interpolation=cv2.INTER_LANCZOS4), sr_u8)
        st.markdown(f"**{m}**")
        st.image(sr_u8, use_container_width=True, clamp=True)
        st.caption(f"PSNR: {p:.1f} dB · {sr_u8.shape[1]}×{sr_u8.shape[0]}")

st.markdown("---")

# ── Detailed comparison with slider ────────────────────────────────────────────
st.markdown("### Step 3: Side-by-Side Comparison Slider")
m1 = st.selectbox("Left method",  methods, index=0)
m2 = st.selectbox("Right method", methods, index=4)

comparison_slider(results[m1], results[m2],
                  label_before=m1, label_after=m2, key="sr_compare")

st.markdown("---")

# ── Quality metrics table ──────────────────────────────────────────────────────
st.markdown("### Step 4: Quality Metrics")
theory_box("PSNR (Peak Signal-to-Noise Ratio): higher = better. Measures pixel-level fidelity. "
           "Sharpness = mean of absolute Laplacian response — higher means more edge detail. "
           "Note: sharpening methods may increase PSNR AND perceived sharpness.")

ref_size = (lr_w * scale, lr_h * scale)
ref_img  = cv2.resize(gray, ref_size, interpolation=cv2.INTER_LANCZOS4)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
psnr_vals = []
sharp_vals = []
for m in methods:
    r = results[m]
    ref_r = cv2.resize(ref_img, (r.shape[1], r.shape[0]))
    psnr_vals.append(psnr(ref_r, r))
    lap = cv2.Laplacian(r.astype(np.float32), cv2.CV_32F)
    sharp_vals.append(np.abs(lap).mean())

colours = ["#94a3b8","#64748b","#3b82f6","#8b5cf6","#22c55e","#f59e0b"]
axes[0].bar(methods, psnr_vals, color=colours, alpha=0.85)
axes[0].set_title("PSNR (dB) — Higher is better")
axes[0].set_ylabel("dB"); axes[0].tick_params(axis="x", rotation=25)
axes[0].set_ylim(min(psnr_vals)-2, max(psnr_vals)+2)

axes[1].bar(methods, sharp_vals, color=colours, alpha=0.85)
axes[1].set_title("Sharpness (Laplacian) — Higher = more detail")
axes[1].set_ylabel("Mean |Laplacian|"); axes[1].tick_params(axis="x", rotation=25)

plt.tight_layout()
fig_to_st(fig)

# Metrics table
st.markdown("**Metrics table:**")
header_cols = st.columns(4)
header_cols[0].markdown("**Method**")
header_cols[1].markdown("**Output size**")
header_cols[2].markdown("**PSNR (dB)**")
header_cols[3].markdown("**Sharpness**")

for i, m in enumerate(methods):
    r = results[m]
    cols_m = st.columns(4)
    cols_m[0].markdown(m)
    cols_m[1].markdown(f"{r.shape[1]}×{r.shape[0]}")
    cols_m[2].markdown(f"{psnr_vals[i]:.2f}")
    cols_m[3].markdown(f"{sharp_vals[i]:.3f}")

st.markdown("---")

# ── Download best result ───────────────────────────────────────────────────────
st.markdown("### Step 5: Download Best Result")
best_method = st.selectbox("Select method to download", methods, index=4)
best_img = results[best_method]
pil_img  = __import__("PIL").Image.fromarray(best_img)
buf      = __import__("io").BytesIO()
pil_img.save(buf, format="PNG"); buf.seek(0)
st.download_button(f"⬇ Download {best_method} result ({scale}×)",
                    buf, f"sr_{best_method.replace(' ','_')}_{scale}x.png", "image/png")
