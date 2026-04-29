import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import io
from PIL import Image
from utils.theme import inject, page_header, theory_card, metric_row
from utils.helpers import upload_image, to_gray, normalize_display

inject("GIF Animator", "✨")


page_header("Parameter Sweep GIF Animator",
            "SWEEP ANY PARAMETER THROUGH ITS RANGE AND EXPORT AS ANIMATED GIF", "✨", "#22d3a5")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


img_rgb = upload_image("gif_up")
gray    = to_gray(img_rgb)

st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ GIF Settings")
fps       = st.sidebar.slider("Frame rate (fps)", 1, 15, 5)
loop      = st.sidebar.checkbox("Loop forever", value=True)
n_frames  = st.sidebar.slider("Number of frames", 8, 60, 20)
scale_pct = st.sidebar.slider("Output scale %", 25, 100, 50)

theory_card(
    "A parameter sweep GIF shows how an image changes as one parameter varies from min to max. "
    "For example, sweeping Gaussian sigma from 0→15 shows progressive blurring. "
    "Each frame is a processed version of the image at a different parameter value. "
    "The frames are assembled into an animated GIF using PIL's image sequence feature."
)

# ── Operation picker ───────────────────────────────────────────────────────────
st.markdown("### Select operation to animate")
op = st.selectbox("Operation", [
    "Gaussian Blur (sigma)",
    "Canny Edges (threshold)",
    "Histogram Equalisation (blend)",
    "CLAHE clip limit",
    "Gamma Correction",
    "Threshold sweep",
    "Erosion (kernel size)",
    "Dilation (kernel size)",
    "Laplacian sharpening",
    "DFT Low-pass cutoff",
    "Pixelation (sampling)",
    "Rotation (angle)",
])

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Original image**")
    st.image(gray, use_container_width=True, clamp=True)

# ── Frame generator ────────────────────────────────────────────────────────────
def gen_frames(op, gray, n):
    frames = []
    if op == "Gaussian Blur (sigma)":
        for s in np.linspace(0.5, 20.0, n):
            f = cv2.GaussianBlur(gray, (0,0), s)
            frames.append((f, f"σ = {s:.1f}"))

    elif op == "Canny Edges (threshold)":
        for t in np.linspace(20, 200, n, dtype=int):
            f = cv2.Canny(gray, int(t), int(t)*2)
            frames.append((f, f"T = {t}"))

    elif op == "Histogram Equalisation (blend)":
        eq = cv2.equalizeHist(gray)
        for a in np.linspace(0, 1, n):
            f = np.clip(gray.astype(float)*(1-a) + eq.astype(float)*a, 0, 255).astype(np.uint8)
            frames.append((f, f"blend = {a:.2f}"))

    elif op == "CLAHE clip limit":
        for c in np.linspace(0.5, 10.0, n):
            clahe = cv2.createCLAHE(clipLimit=c, tileGridSize=(8,8))
            f = clahe.apply(gray)
            frames.append((f, f"clip = {c:.1f}"))

    elif op == "Gamma Correction":
        for g in np.linspace(0.1, 4.0, n):
            lut = np.array([((i/255.0)**g)*255 for i in range(256)], np.uint8)
            f   = cv2.LUT(gray, lut)
            frames.append((f, f"γ = {g:.2f}"))

    elif op == "Threshold sweep":
        for t in np.linspace(0, 255, n, dtype=int):
            _, f = cv2.threshold(gray, int(t), 255, cv2.THRESH_BINARY)
            frames.append((f, f"T = {t}"))

    elif op == "Erosion (kernel size)":
        for k in range(1, n+1, max(1, n//20)):
            ks = k*2+1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks,ks))
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            f = cv2.erode(binary, kernel)
            frames.append((f, f"SE = {ks}×{ks}"))
        frames = frames[:n]

    elif op == "Dilation (kernel size)":
        for k in range(1, n+1, max(1, n//20)):
            ks = k*2+1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks,ks))
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            f = cv2.dilate(binary, kernel)
            frames.append((f, f"SE = {ks}×{ks}"))
        frames = frames[:n]

    elif op == "Laplacian sharpening":
        lap = cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F)
        for w in np.linspace(0, 2.5, n):
            f = np.clip(gray.astype(float) - w*lap, 0, 255).astype(np.uint8)
            frames.append((f, f"w = {w:.2f}"))

    elif op == "DFT Low-pass cutoff":
        rows, cols = gray.shape; crow,ccol = rows//2, cols//2
        Y,X = np.ogrid[:rows,:cols]
        D   = np.sqrt((Y-crow)**2+(X-ccol)**2)
        F   = np.fft.fftshift(np.fft.fft2(gray.astype(float)))
        for d0 in np.linspace(5, min(rows,cols)//2, n):
            H = np.exp(-(D**2)/(2*d0**2))
            f = normalize_display(np.abs(np.fft.ifft2(np.fft.ifftshift(F*H))))
            frames.append((f, f"D₀ = {d0:.0f}"))

    elif op == "Pixelation (sampling)":
        for factor in np.linspace(1, 32, n, dtype=int):
            f_int = max(1, int(factor))
            small = cv2.resize(gray, (max(1,gray.shape[1]//f_int), max(1,gray.shape[0]//f_int)), interpolation=cv2.INTER_NEAREST)
            f     = cv2.resize(small, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_NEAREST)
            frames.append((f, f"×{f_int}"))

    elif op == "Rotation (angle)":
        h, w = gray.shape
        for angle in np.linspace(0, 360, n, endpoint=False):
            M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
            f = cv2.warpAffine(gray, M, (w, h))
            frames.append((f, f"{angle:.0f}°"))

    return frames

with col2:
    st.markdown("**Preview (first frame)**")
    preview_frames = gen_frames(op, gray, 4)
    if preview_frames:
        st.image(preview_frames[0][0], caption=preview_frames[0][1],
                 use_container_width=True, clamp=True)

st.markdown("---")

# ── Generate GIF ───────────────────────────────────────────────────────────────
if st.button("🎬 Generate Animated GIF"):
    with st.spinner(f"Generating {n_frames} frames..."):
        frames = gen_frames(op, gray, n_frames)

        # Add text label to each frame
        labeled = []
        for frame_img, label in frames:
            f = np.clip(frame_img, 0, 255).astype(np.uint8)
            if len(f.shape) == 2:
                f = cv2.cvtColor(f, cv2.COLOR_GRAY2RGB)

            # Downscale
            new_w = max(50, int(f.shape[1] * scale_pct / 100))
            new_h = max(50, int(f.shape[0] * scale_pct / 100))
            f     = cv2.resize(f, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

            # Label overlay
            cv2.rectangle(f, (0, f.shape[0]-22), (f.shape[1], f.shape[0]), (20,20,30), -1)
            cv2.putText(f, label, (6, f.shape[0]-6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100,200,255), 1, cv2.LINE_AA)
            labeled.append(Image.fromarray(f))

        # Save GIF
        gif_buf = io.BytesIO()
        duration_ms = int(1000 / fps)
        labeled[0].save(gif_buf, format="GIF", save_all=True,
                        append_images=labeled[1:],
                        duration=duration_ms, loop=0 if loop else 1,
                        optimize=True)
        gif_buf.seek(0)
        gif_bytes = gif_buf.read()

    st.success(f"✅ GIF created! {n_frames} frames at {fps} fps — {len(gif_bytes)//1024} KB")

    # Display in browser
    import base64
    b64 = base64.b64encode(gif_bytes).decode()
    st.markdown(f"""
    <div style="text-align:center;margin:16px 0">
      <img src="data:image/gif;base64,{b64}"
           style="max-width:100%;border-radius:10px;border:1px solid #2a3a55"/>
      <div style="font-size:0.78rem;color:#64748b;margin-top:6px">
        {n_frames} frames · {fps} fps · {len(gif_bytes)//1024} KB
      </div>
    </div>""", unsafe_allow_html=True)

    st.download_button(
        f"⬇ Download GIF ({len(gif_bytes)//1024} KB)",
        gif_bytes,
        f"dip_{op.replace(' ','_').replace('(','').replace(')','').lower()}_sweep.gif",
        "image/gif"
    )

    metric_row([
        ("Frames",    str(n_frames)),
        ("FPS",       str(fps)),
        ("Size",      f"{len(gif_bytes)//1024} KB"),
        ("Duration",  f"{n_frames/fps:.1f}s"),
        ("Scale",     f"{scale_pct}%"),
    ])
