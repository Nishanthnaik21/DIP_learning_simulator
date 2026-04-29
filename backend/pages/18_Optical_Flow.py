import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from utils.theme import inject, page_header, theory_card, metric_row
from utils.helpers import upload_image, to_gray, fig_to_st

inject("Optical Flow", "🌊")


page_header("Optical Flow — Motion Estimation",
            "LUCAS-KANADE SPARSE FLOW · FARNEBACK DENSE FLOW · MOTION VISUALISATION", "🌊", "#22d3a5")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "Optical flow estimates the apparent motion of pixels between two consecutive frames. "
    "Lucas-Kanade (sparse): tracks specific keypoints using local window-based least squares. "
    "Assumes constant brightness and small motion. Best for tracking feature points. "
    "Farneback (dense): computes flow for EVERY pixel using polynomial expansion approximation. "
    "Gives a complete motion field — useful for action recognition and scene flow."
)

# ── Image inputs ───────────────────────────────────────────────────────────────
st.markdown("### Input: Two Consecutive Frames")
st.markdown("""
<div style="background:rgba(34,211,165,0.08);border:1px solid rgba(34,211,165,0.25);
            border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:0.83rem;color:#6ee7b7">
  Upload two frames of a video, or two slightly different photos of the same scene.
  If you only upload one image, a synthetic motion version is created for demonstration.
</div>""", unsafe_allow_html=True)

col_u1, col_u2 = st.columns(2)
with col_u1:
    file1 = st.file_uploader("Frame 1 (first)", type=["jpg","jpeg","png"], key="flow1")
with col_u2:
    file2 = st.file_uploader("Frame 2 (second)", type=["jpg","jpeg","png"], key="flow2")

# Load frames
if file1:
    from PIL import Image as PILImage
    frame1 = cv2.cvtColor(np.array(PILImage.open(file1).convert("RGB")), cv2.COLOR_RGB2GRAY)
else:
    frame1 = to_gray(upload_image("flow_default"))

if file2:
    from PIL import Image as PILImage
    frame2 = cv2.cvtColor(np.array(PILImage.open(file2).convert("RGB")), cv2.COLOR_RGB2GRAY)
else:
    # Synthetic motion: slight translation + rotation
    tx = st.slider("Synthetic translation X", -30, 30, 8, help="Simulates horizontal motion")
    ty = st.slider("Synthetic translation Y", -30, 30, 4, help="Simulates vertical motion")
    M  = np.float32([[1, 0, tx], [0, 1, ty]])
    frame2 = cv2.warpAffine(frame1, M, (frame1.shape[1], frame1.shape[0]))
    st.info(f"Using synthetic motion: translate ({tx},{ty}) pixels")

# Resize to same size
H = min(frame1.shape[0], frame2.shape[0], 256)
W = min(frame1.shape[1], frame2.shape[1], 256)
frame1 = cv2.resize(frame1, (W, H))
frame2 = cv2.resize(frame2, (W, H))

# Show frames
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Frame 1**"); st.image(frame1, use_container_width=True, clamp=True)
with c2:
    st.markdown("**Frame 2**"); st.image(frame2, use_container_width=True, clamp=True)

st.markdown("---")

# ── Method selector ────────────────────────────────────────────────────────────
method = st.radio("Flow method", ["Lucas-Kanade (Sparse)", "Farneback (Dense)"], horizontal=True)

tab1, tab2 = st.tabs(["📊 Flow Visualisation", "📐 Analysis"])

with tab1:
    if method == "Lucas-Kanade (Sparse)":
        max_corners = st.slider("Max feature points", 20, 500, 100)
        quality     = st.slider("Quality level", 0.001, 0.1, 0.01, format="%.3f")
        win_size    = st.slider("Window size", 5, 31, 15, step=2)

        # Detect features in frame1
        p0 = cv2.goodFeaturesToTrack(frame1, maxCorners=max_corners,
                                      qualityLevel=quality, minDistance=7,
                                      blockSize=7)
        if p0 is not None and len(p0) > 0:
            p1, st_flag, err = cv2.calcOpticalFlowPyrLK(
                frame1, frame2, p0, None,
                winSize=(win_size, win_size),
                maxLevel=3,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
            )
            good_new = p1[st_flag == 1]
            good_old = p0[st_flag == 1]

            # Draw on colour overlay
            overlay = cv2.cvtColor(frame1, cv2.COLOR_GRAY2RGB)
            for new, old in zip(good_new, good_old):
                a, b = new.ravel().astype(int)
                c_, d = old.ravel().astype(int)
                cv2.arrowedLine(overlay, (c_, d), (a, b), (0, 220, 120), 2, tipLength=0.3)
                cv2.circle(overlay, (a, b), 3, (79, 142, 247), -1)

            magnitudes = np.sqrt((good_new[:,0]-good_old[:,0])**2 + (good_new[:,1]-good_old[:,1])**2)
            st.image(overlay, caption=f"Lucas-Kanade flow ({len(good_new)} tracked points)", use_container_width=True)
            metric_row([
                ("Points tracked",  len(good_new)),
                ("Mean motion",     f"{magnitudes.mean():.1f} px"),
                ("Max motion",      f"{magnitudes.max():.1f} px"),
                ("Window size",     f"{win_size}×{win_size}"),
            ])
            theory_card(
                f"Lucas-Kanade: tracked {len(good_new)}/{len(p0)} feature points. "
                f"Green arrows show displacement vectors. Blue dots = new positions. "
                f"Mean motion = {magnitudes.mean():.1f} pixels per frame."
            )
        else:
            st.warning("No feature points detected. Try lowering the quality level.")

    else:  # Farneback Dense
        pyr_scale = st.slider("Pyramid scale", 0.3, 0.9, 0.5)
        levels    = st.slider("Pyramid levels", 1, 6, 3)
        winsize   = st.slider("Window size",    5, 31, 15, step=2)
        poly_n    = st.select_slider("Poly N", [5, 7], 5)

        flow = cv2.calcOpticalFlowFarneback(
            frame1, frame2, None,
            pyr_scale, levels, winsize,
            3, poly_n, 1.1, 0
        )
        fx, fy = flow[..., 0], flow[..., 1]
        mag, ang = cv2.cartToPolar(fx, fy)

        # HSV colour-coded flow
        hsv = np.zeros((H, W, 3), dtype=np.uint8)
        hsv[..., 1] = 255
        hsv[..., 0] = (ang * 180 / np.pi / 2).astype(np.uint8)
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        flow_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

        # Quiver overlay
        step      = max(4, W//32)
        overlay_q = cv2.cvtColor(frame1, cv2.COLOR_GRAY2RGB)
        for y in range(0, H, step):
            for x in range(0, W, step):
                dx, dy = int(fx[y, x] * 3), int(fy[y, x] * 3)
                if abs(dx) + abs(dy) > 1:
                    cv2.arrowedLine(overlay_q, (x, y), (x+dx, y+dy),
                                    (0, 220, 120), 1, tipLength=0.4)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**HSV Flow Map (hue=direction, brightness=speed)**")
            st.image(flow_rgb, use_container_width=True)
        with c2:
            st.markdown("**Quiver Plot (motion vectors)**")
            st.image(overlay_q, use_container_width=True)

        metric_row([
            ("Mean flow magnitude", f"{mag.mean():.2f} px"),
            ("Max flow magnitude",  f"{mag.max():.2f} px"),
            ("Flow coverage",        f"{(mag>0.5).mean()*100:.1f}%"),
        ])
        theory_card(
            "Farneback dense flow: HSV colour coding — hue encodes direction (0°=red=right, "
            "90°=green=up, 180°=cyan=left, 270°=magenta=down), brightness encodes speed. "
            f"Mean motion = {mag.mean():.2f} px/frame."
        )

with tab2:
    # Flow magnitude histogram
    if method == "Farneback (Dense)":
        flow_dense = cv2.calcOpticalFlowFarneback(frame1, frame2, None, 0.5, 3, 15, 3, 5, 1.1, 0)
        fx2, fy2   = flow_dense[...,0], flow_dense[...,1]
        mag2, ang2 = cv2.cartToPolar(fx2, fy2)

        fig, axes = plt.subplots(1, 2, figsize=(12, 4), facecolor="#0b0f1a")
        for ax in axes: ax.set_facecolor("#1a2235")
        axes[0].hist(mag2.flatten(), bins=60, color="#22d3a5", alpha=0.85)
        axes[0].set_title("Motion magnitude distribution", color="#e2e8f0")
        axes[0].set_xlabel("Pixels/frame", color="#94a3b8"); axes[0].tick_params(colors="#64748b")
        for s in axes[0].spines.values(): s.set_color("#2a3a55")
        axes[1].hist(np.degrees(ang2.flatten()), bins=72, range=(0,360), color="#4f8ef7", alpha=0.85)
        axes[1].set_title("Motion direction distribution", color="#e2e8f0")
        axes[1].set_xlabel("Direction (degrees)", color="#94a3b8"); axes[1].tick_params(colors="#64748b")
        for s in axes[1].spines.values(): s.set_color("#2a3a55")
        plt.tight_layout(); fig_to_st(fig)
    else:
        st.info("Switch to Farneback (Dense) flow for the analysis tab.")
