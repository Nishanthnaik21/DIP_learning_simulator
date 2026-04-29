import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import io
import zipfile
from PIL import Image
from utils.theme import inject, page_header, theory_card, metric_row
from utils.helpers import to_gray, normalize_display, psnr

inject("Batch Processing", "📦")


page_header("Batch Image Processing",
            "UPLOAD MULTIPLE IMAGES AND APPLY THE SAME OPERATION TO ALL AT ONCE", "📦", "#fbbf24")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "Batch processing applies a single DIP pipeline to multiple images automatically. "
    "Upload up to 20 images, choose an operation and parameters, and all results are "
    "processed simultaneously. Download the full set as a ZIP file. "
    "Useful for dataset augmentation, consistent preprocessing, and automated pipelines."
)

# ── Upload ─────────────────────────────────────────────────────────────────────
st.markdown("### 📁 Upload Images")
uploaded_files = st.file_uploader(
    "Upload multiple images (JPG/PNG) — up to 20",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.markdown("""
    <div style="background:#1a2235;border:2px dashed #2a3a55;border-radius:10px;
                padding:40px 20px;text-align:center">
      <div style="font-size:2.5rem;margin-bottom:10px">📦</div>
      <div style="color:#94a3b8;font-size:0.9rem;font-weight:600">Drop multiple images here</div>
      <div style="color:#64748b;font-size:0.8rem;margin-top:4px">Supports JPG, PNG — up to 20 files</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

files = uploaded_files[:20]
st.success(f"✅ {len(files)} image(s) loaded")

# Show thumbnails
st.markdown("#### Input images")
thumb_cols = st.columns(min(len(files), 6))
for i, f in enumerate(files[:6]):
    with thumb_cols[i]:
        img = Image.open(f).convert("RGB")
        st.image(img, caption=f.name[:16], use_container_width=True)
if len(files) > 6:
    st.caption(f"+ {len(files)-6} more images")

# ── Operation ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### ⚙️ Choose Operation")

op = st.selectbox("Operation to apply to ALL images", [
    "Greyscale conversion",
    "Gaussian Blur",
    "Canny Edge Detection",
    "Histogram Equalisation",
    "CLAHE Enhancement",
    "Resize to fixed size",
    "Gamma Correction",
    "Otsu Threshold",
    "Sharpen",
    "Negative",
    "Pseudo-colour (Jet)",
    "Pencil Sketch",
])

params_ui = {}
if op == "Gaussian Blur":
    k = st.slider("Kernel size", 3, 31, 9, step=2)
    s = st.slider("Sigma", 0.5, 10.0, 2.0)
    params_ui = {"ksize": k, "sigma": s}
elif op == "Canny Edge Detection":
    t1 = st.slider("Low T",  10, 200, 50)
    t2 = st.slider("High T", 50, 400, 150)
    params_ui = {"t1": t1, "t2": t2}
elif op == "CLAHE Enhancement":
    clip = st.slider("Clip limit", 1.0, 8.0, 2.5)
    tile = st.slider("Tile size",  4, 16, 8)
    params_ui = {"clip": clip, "tile": tile}
elif op == "Resize to fixed size":
    rw = st.slider("Width",  64, 1024, 256, step=32)
    rh = st.slider("Height", 64, 1024, 256, step=32)
    params_ui = {"width": rw, "height": rh}
elif op == "Gamma Correction":
    gamma = st.slider("Gamma γ", 0.1, 4.0, 1.5)
    params_ui = {"gamma": gamma}

# ── Process function ───────────────────────────────────────────────────────────
def process_one(img_rgb: np.ndarray, op: str, p: dict) -> np.ndarray:
    gray = to_gray(img_rgb)
    if op == "Greyscale conversion":
        return gray
    elif op == "Gaussian Blur":
        return cv2.GaussianBlur(img_rgb, (p["ksize"],p["ksize"]), p["sigma"])
    elif op == "Canny Edge Detection":
        return cv2.Canny(gray, p["t1"], p["t2"])
    elif op == "Histogram Equalisation":
        return cv2.equalizeHist(gray)
    elif op == "CLAHE Enhancement":
        clahe = cv2.createCLAHE(clipLimit=p["clip"], tileGridSize=(p["tile"],p["tile"]))
        return clahe.apply(gray)
    elif op == "Resize to fixed size":
        return cv2.resize(img_rgb, (p["width"], p["height"]), interpolation=cv2.INTER_LANCZOS4)
    elif op == "Gamma Correction":
        lut = np.array([((i/255.0)**p["gamma"])*255 for i in range(256)], np.uint8)
        if len(img_rgb.shape)==3:
            out = np.zeros_like(img_rgb)
            for c in range(3): out[:,:,c] = cv2.LUT(img_rgb[:,:,c], lut)
            return out
        return cv2.LUT(gray, lut)
    elif op == "Otsu Threshold":
        _, out = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return out
    elif op == "Sharpen":
        k = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]], np.float32)
        return np.clip(cv2.filter2D(img_rgb.astype(np.float32),-1,k),0,255).astype(np.uint8)
    elif op == "Negative":
        return 255 - img_rgb
    elif op == "Pseudo-colour (Jet)":
        pseudo = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        return cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB)
    elif op == "Pencil Sketch":
        blur = cv2.GaussianBlur(gray, (21,21), 0)
        return cv2.divide(gray, blur, scale=256)
    return img_rgb

# ── Run batch ──────────────────────────────────────────────────────────────────
if st.button("🚀 Run Batch Processing"):
    results = []
    progress = st.progress(0)
    status   = st.empty()

    for i, f in enumerate(files):
        f.seek(0)
        img_pil = Image.open(f).convert("RGB")
        img_arr = np.array(img_pil)
        result  = process_one(img_arr, op, params_ui)
        results.append((f.name, result))
        progress.progress((i+1)/len(files))
        status.text(f"Processing {i+1}/{len(files)}: {f.name}")

    status.empty(); progress.empty()
    st.success(f"✅ Processed {len(results)} images!")

    # Preview results
    st.markdown("#### Results Preview")
    prev_cols = st.columns(min(len(results), 5))
    psnr_sum = 0
    for i, (fname, res) in enumerate(results[:5]):
        with prev_cols[i]:
            disp = np.clip(res, 0, 255).astype(np.uint8)
            st.image(disp, caption=fname[:14], use_container_width=True, clamp=True)

    # Stats
    st.markdown("#### Batch Statistics")
    sizes = []
    for fname, res in results:
        pil_r = Image.fromarray(np.clip(res,0,255).astype(np.uint8))
        buf_r = io.BytesIO(); pil_r.save(buf_r, format="PNG"); sizes.append(len(buf_r.getvalue()))

    metric_row([
        ("Images processed", str(len(results))),
        ("Operation",        op.split("(")[0].strip()),
        ("Avg output size",  f"{int(np.mean(sizes))//1024} KB"),
        ("Total output",     f"{sum(sizes)//1024} KB"),
    ])

    # Build ZIP
    st.markdown("---")
    st.markdown("#### 📦 Download All Results")
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname, res in results:
            pil_r = Image.fromarray(np.clip(res,0,255).astype(np.uint8))
            img_buf = io.BytesIO()
            fmt = "PNG" if pil_r.mode == "L" else "PNG"
            pil_r.save(img_buf, format=fmt)
            base = os.path.splitext(fname)[0]
            zf.writestr(f"processed_{base}.png", img_buf.getvalue())

        # Add a log file
        log = f"Batch Processing Log\n{'='*40}\n"
        log += f"Operation: {op}\n"
        log += f"Parameters: {params_ui}\n"
        log += f"Files processed: {len(results)}\n\n"
        for fname, _ in results:
            log += f"  - {fname}\n"
        zf.writestr("batch_log.txt", log)

    zip_buf.seek(0)
    st.download_button(
        f"⬇ Download ZIP ({len(results)} images)",
        zip_buf,
        f"batch_{op.replace(' ','_').lower()[:20]}.zip",
        "application/zip"
    )
