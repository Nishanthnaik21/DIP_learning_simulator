import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import io
from PIL import Image
from utils.theme import inject, page_header, theory_card, metric_row
from utils.helpers import to_gray, normalize_display, psnr, comparison_slider

inject("Webcam Capture", "📷")


page_header("Webcam Live Capture", "USE YOUR CAMERA AS A LIVE DIP INPUT SOURCE", "📷", "#22d3a5")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


st.markdown("""
<div style="background:rgba(34,211,165,0.08);border:1px solid rgba(34,211,165,0.25);
            border-radius:10px;padding:12px 16px;margin-bottom:18px;font-size:0.85rem;color:#6ee7b7">
  📷 <b>How it works:</b> Click <b>Take Photo</b> to capture a frame from your webcam.
  The captured image becomes the input for any DIP operation below — processed in real time.
  Your camera feed stays in your browser; no data is sent anywhere.
</div>
""", unsafe_allow_html=True)

# ── Camera input ───────────────────────────────────────────────────────────────
col_cam, col_proc = st.columns([1, 1])

with col_cam:
    st.markdown("#### 📷 Camera Input")
    camera_image = st.camera_input("Take a photo")

    if camera_image is None:
        st.markdown("""
        <div style="background:#1a2235;border:2px dashed #2a3a55;border-radius:10px;
                    padding:40px 20px;text-align:center;margin-top:12px">
          <div style="font-size:2.5rem;margin-bottom:8px">📷</div>
          <div style="color:#64748b;font-size:0.85rem">Allow camera access and click the button above</div>
        </div>""", unsafe_allow_html=True)

img_array = None
if camera_image is not None:
    img_pil   = Image.open(camera_image).convert("RGB")
    img_array = np.array(img_pil)
    gray      = to_gray(img_array)

    with col_cam:
        metric_row([
            ("Size", f"{img_array.shape[1]}×{img_array.shape[0]}"),
            ("Mean", f"{gray.mean():.1f}"),
            ("Std",  f"{gray.std():.1f}"),
        ])

    # ── Processing ─────────────────────────────────────────────────────────────
    with col_proc:
        st.markdown("#### ⚙️ Real-time Processing")
        op = st.selectbox("Apply operation", [
            "None (show original)",
            "Greyscale",
            "Gaussian Blur",
            "Canny Edge Detection",
            "Histogram Equalisation",
            "CLAHE Enhancement",
            "Pseudo-colour (Jet)",
            "Pencil Sketch",
            "Emboss Effect",
            "Cartoonify",
            "Sharpen",
            "Negative",
            "Otsu Threshold",
            "Harris Corners",
            "Colour Quantisation (k-means)",
        ])

        params = {}

        if op == "None (show original)":
            result = img_array

        elif op == "Greyscale":
            result = gray

        elif op == "Gaussian Blur":
            ksize = st.slider("Kernel size", 3, 51, 15, step=2)
            sigma = st.slider("Sigma", 0.5, 15.0, 3.0)
            result = cv2.GaussianBlur(img_array, (ksize, ksize), sigma)
            params = {"Kernel": ksize, "Sigma": sigma}

        elif op == "Canny Edge Detection":
            t1 = st.slider("Low threshold",  10, 200, 50)
            t2 = st.slider("High threshold", 50, 400, 150)
            result = cv2.Canny(gray, t1, t2)
            params = {"Low T": t1, "High T": t2}

        elif op == "Histogram Equalisation":
            result = cv2.equalizeHist(gray)

        elif op == "CLAHE Enhancement":
            clip = st.slider("Clip limit", 1.0, 8.0, 2.5)
            tile = st.slider("Tile size", 4, 16, 8)
            clahe  = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
            result = clahe.apply(gray)
            params = {"Clip": clip, "Tile": tile}

        elif op == "Pseudo-colour (Jet)":
            pseudo = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            result = cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB)

        elif op == "Pencil Sketch":
            blur    = cv2.GaussianBlur(gray, (21, 21), 0)
            result  = cv2.divide(gray, blur, scale=256)

        elif op == "Emboss Effect":
            kernel = np.array([[-2,-1,0],[-1,1,1],[0,1,2]], dtype=np.float32)
            result = np.clip(cv2.filter2D(gray.astype(np.float32), -1, kernel) + 128, 0, 255).astype(np.uint8)

        elif op == "Cartoonify":
            blur  = cv2.bilateralFilter(img_array, 9, 75, 75)
            edges = cv2.Canny(gray, 50, 150)
            edges3 = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            result = cv2.bitwise_and(blur, cv2.bitwise_not(edges3))

        elif op == "Sharpen":
            kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]], dtype=np.float32)
            result = np.clip(cv2.filter2D(img_array.astype(np.float32), -1, kernel), 0, 255).astype(np.uint8)

        elif op == "Negative":
            result = 255 - img_array

        elif op == "Otsu Threshold":
            _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        elif op == "Harris Corners":
            dst     = cv2.cornerHarris(gray, 2, 3, 0.04)
            dst     = cv2.dilate(dst, None)
            result  = img_array.copy()
            result[dst > 0.01 * dst.max()] = [255, 50, 50]

        elif op == "Colour Quantisation (k-means)":
            k    = st.slider("Number of colours k", 2, 16, 6)
            data = img_array.reshape((-1, 3)).astype(np.float32)
            _, labels, centers = cv2.kmeans(
                data, k, None,
                (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
                3, cv2.KMEANS_RANDOM_CENTERS
            )
            result = centers[labels.flatten()].reshape(img_array.shape).astype(np.uint8)
            params = {"k colours": k}
        else:
            result = img_array

        result_u8 = np.clip(result, 0, 255).astype(np.uint8)
        st.image(result_u8, caption=f"Result: {op}", use_container_width=True, clamp=True)

        # Download
        pil_out = Image.fromarray(result_u8)
        buf = io.BytesIO(); pil_out.save(buf, format="PNG"); buf.seek(0)
        st.download_button("⬇ Download processed image", buf,
                           f"webcam_{op.replace(' ','_').lower()}.png", "image/png")

    # ── Comparison slider ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ↔️ Before / After Comparison")
    before_disp = gray if len(np.array(img_array).shape) < 3 else img_array
    after_disp  = result_u8
    comparison_slider(before_disp, after_disp, "Original", op, key=f"wc_{op}")

    # ── Theory ────────────────────────────────────────────────────────────────
    theories = {
        "Greyscale":                "RGB→Grey using Y = 0.299R + 0.587G + 0.114B luminance formula.",
        "Gaussian Blur":            "Convolution with Gaussian kernel G(x,y)=e^(-(x²+y²)/2σ²). Reduces high-frequency noise.",
        "Canny Edge Detection":     "Multi-stage: Gaussian smooth → Sobel gradient → Non-maximum suppression → Double threshold → Hysteresis.",
        "Histogram Equalisation":   "Maps intensities via CDF so output histogram is approximately uniform — maximises contrast.",
        "CLAHE Enhancement":        "Local equalisation in tiles with histogram clipping — avoids over-amplification of noise.",
        "Pseudo-colour (Jet)":      "Each grey intensity maps to a colour via a lookup table. Enhances visual discrimination without adding real colour info.",
        "Pencil Sketch":            "Divide original grey by its Gaussian blur — bright/flat areas become white, edges become dark lines.",
        "Emboss Effect":            "Directional convolution kernel produces a raised relief effect — highlights edges in one direction.",
        "Cartoonify":               "Bilateral filter preserves edges while smoothing — Canny extracts edges — edges overlaid as black lines.",
        "Sharpen":                  "Kernel [0,-1,0;-1,5,-1;0,-1,0] subtracts a weighted Laplacian, amplifying edge transitions.",
        "Negative":                 "I_out = 255 − I_in. Inverts all intensity values — dark regions become bright and vice versa.",
        "Otsu Threshold":           "Automatically finds threshold T that minimises intra-class variance of the bimodal histogram.",
        "Harris Corners":           "R = det(M) − k·trace(M)². Large positive R → corner. Marked in red on the image.",
        "Colour Quantisation (k-means)": "K-means clustering groups pixels into k colour clusters — reduces palette while preserving overall structure.",
    }
    if op in theories:
        theory_card(theories[op])

else:
    with col_proc:
        st.markdown("#### ⚙️ Processing")
        st.markdown("""
        <div style="background:#1a2235;border:2px dashed #2a3a55;border-radius:10px;
                    padding:40px 20px;text-align:center;margin-top:12px">
          <div style="font-size:2rem;margin-bottom:8px">🔄</div>
          <div style="color:#64748b;font-size:0.85rem">Capture a photo first to see processing options</div>
        </div>""", unsafe_allow_html=True)
