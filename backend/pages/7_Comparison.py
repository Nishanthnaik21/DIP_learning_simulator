import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
from utils.helpers import *



st.set_page_config(page_title="Before/After Comparison", page_icon="↔️", layout="wide")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj

st.markdown("## ↔️ Before / After Comparison Slider")
st.caption("Apply any DIP operation and drag the slider to compare original vs processed side by side")
st.markdown("---")

img_rgb = upload_image("compare_upload")
gray    = to_gray(img_rgb)

# ── Operation picker ───────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Operation")
category = st.sidebar.selectbox("Category", [
    "Spatial Filters",
    "Histogram Processing",
    "Frequency Filters",
    "Noise & Restoration",
    "Edge Detection",
    "Morphological Ops",
    "Colour Processing",
    "Intensity Transforms",
])

st.markdown(f"### Category: {category}")

before = gray.copy()
after  = gray.copy()
op_name = "Identity"
params  = {}
theory  = ""

# ── Operations ─────────────────────────────────────────────────────────────────
if category == "Spatial Filters":
    op = st.selectbox("Filter", ["Gaussian Blur","Median Filter","Bilateral Filter","Average Filter"])
    ksize = st.slider("Kernel size", 3, 31, 9, step=2)
    if op == "Gaussian Blur":
        sigma = st.slider("Sigma", 0.5, 10.0, 2.0)
        after  = cv2.GaussianBlur(gray, (ksize,ksize), sigma)
        params = {"Kernel":f"{ksize}×{ksize}", "Sigma":sigma}
        theory = f"Gaussian blur with σ={sigma} reduces noise while preserving general shapes."
    elif op == "Median Filter":
        after  = cv2.medianBlur(gray, ksize)
        params = {"Kernel":f"{ksize}×{ksize}"}
        theory = "Median filter replaces each pixel with the neighbourhood median — removes salt-and-pepper noise without blurring edges."
    elif op == "Bilateral Filter":
        sc = st.slider("Sigma colour", 10, 150, 75)
        ss = st.slider("Sigma space", 10, 150, 75)
        after  = cv2.bilateralFilter(gray, ksize, sc, ss)
        params = {"Diameter":ksize, "Sigma colour":sc, "Sigma space":ss}
        theory = "Bilateral filter smooths while preserving edges by weighing neighbours by spatial distance AND intensity similarity."
    else:
        after  = cv2.blur(gray, (ksize,ksize))
        params = {"Kernel":f"{ksize}×{ksize}"}
        theory = f"Box filter: each pixel = average of {ksize}×{ksize} neighbours."
    op_name = op

elif category == "Histogram Processing":
    op = st.selectbox("Method", ["Histogram Equalisation","CLAHE"])
    if op == "Histogram Equalisation":
        after  = cv2.equalizeHist(gray)
        params = {}
        theory = "HE redistributes pixel intensities so the cumulative histogram becomes linear — maximises global contrast."
    else:
        clip = st.slider("Clip limit", 1.0, 10.0, 2.0)
        tile = st.slider("Tile size", 2, 16, 8)
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile,tile))
        after  = clahe.apply(gray)
        params = {"Clip limit":clip, "Tile":f"{tile}×{tile}"}
        theory = f"CLAHE applies equalisation locally in {tile}×{tile} tiles and clips histogram at {clip} to prevent noise over-amplification."
    op_name = op

elif category == "Frequency Filters":
    ftype = st.selectbox("Filter type", ["Gaussian LP","Gaussian HP","Butterworth LP","Butterworth HP"])
    D0    = st.slider("Cut-off D₀", 5, min(gray.shape)//2, 30)
    rows, cols = gray.shape; crow,ccol = rows//2,cols//2
    Y,X = np.ogrid[:rows,:cols]
    D   = np.sqrt((Y-crow)**2 + (X-ccol)**2)
    if ftype == "Gaussian LP":
        H = np.exp(-(D**2)/(2*D0**2))
        theory = f"Gaussian LPF: H=e^(-D²/2D₀²), D₀={D0}. Smooths image, no ringing."
    elif ftype == "Gaussian HP":
        H = 1 - np.exp(-(D**2)/(2*D0**2))
        theory = f"Gaussian HPF: H=1-e^(-D²/2D₀²), D₀={D0}. Enhances edges."
    elif ftype == "Butterworth LP":
        n = st.slider("Order", 1, 8, 2)
        H = 1 / (1 + (D/D0)**(2*n))
        theory = f"Butterworth LPF order {n}: controlled transition band, minimal ringing."
        params = {"D₀":D0,"Order":n}
    else:
        n = st.slider("Order", 1, 8, 2)
        H = 1 - 1/(1 + (D/D0)**(2*n))
        theory = f"Butterworth HPF order {n}: enhances high-frequency edges, D₀={D0}."
        params = {"D₀":D0,"Order":n}
    F = np.fft.fftshift(np.fft.fft2(gray.astype(float)))
    after = normalize_display(np.abs(np.fft.ifft2(np.fft.ifftshift(F*H))))
    op_name = ftype
    if not params: params = {"D₀":D0}

elif category == "Noise & Restoration":
    op = st.selectbox("Operation", ["Add Gaussian Noise","Add Salt & Pepper","Wiener-style Restoration"])
    if op == "Add Gaussian Noise":
        sigma = st.slider("Noise σ", 5, 80, 20)
        noisy = np.clip(gray.astype(float) + np.random.normal(0,sigma,gray.shape),0,255).astype(np.uint8)
        after  = noisy
        params = {"Sigma":sigma}
        theory = f"Gaussian noise N(0,{sigma}²) added — models electronic sensor noise."
    elif op == "Add Salt & Pepper":
        prob = st.slider("Probability", 0.01, 0.3, 0.05)
        noisy = gray.copy()
        mask  = np.random.rand(*gray.shape)
        noisy[mask < prob/2] = 0; noisy[mask > 1-prob/2] = 255
        after  = noisy
        params = {"Probability":prob}
        theory = "Salt & pepper: random black/white pixels — models transmission errors."
    else:
        sigma_n = st.slider("Noise σ", 5, 50, 15)
        K = st.slider("Wiener K", 0.001, 0.5, 0.01, format="%.3f")
        psf = np.zeros_like(gray.astype(float)); psf[gray.shape[0]//2, :10] = 1/10
        H2  = np.fft.fft2(psf)
        G   = H2 * np.fft.fft2(gray.astype(float))
        G  += np.fft.fft2(np.random.normal(0,sigma_n,gray.shape))
        Hw  = np.conj(H2)/(np.abs(H2)**2+K)
        restored = np.abs(np.fft.ifft2(Hw * G))
        after  = normalize_display(restored)
        params = {"Noise σ":sigma_n, "K":K}
        theory = f"Wiener filter Ĥ=H*/(|H|²+K). K={K:.3f} balances restoration vs noise amplification."
    op_name = op

elif category == "Edge Detection":
    detector = st.selectbox("Detector", ["Canny","Sobel","Laplacian","LoG"])
    if detector == "Canny":
        t1 = st.slider("Low threshold",  10, 200, 50)
        t2 = st.slider("High threshold", 50, 400, 150)
        after  = cv2.Canny(gray, t1, t2)
        params = {"Low T":t1,"High T":t2}
        theory = f"Canny: Gaussian smooth → Sobel gradient → NMS → double threshold [{t1},{t2}] → hysteresis."
    elif detector == "Sobel":
        sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        after  = cv2.convertScaleAbs(np.sqrt(sx**2+sy**2))
        params = {"Kernel":"3×3"}
        theory = "Combined Sobel: magnitude = √(Gx²+Gy²). Detects edges in all directions."
    elif detector == "Laplacian":
        after  = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_32F))
        params = {"Kernel":"3×3"}
        theory = "Laplacian ∇²f: second derivative — detects all edges simultaneously (isotropic)."
    else:
        sigma = st.slider("LoG sigma", 0.5, 5.0, 1.5)
        smooth = cv2.GaussianBlur(gray, (9,9), sigma)
        after  = cv2.convertScaleAbs(cv2.Laplacian(smooth, cv2.CV_32F))
        params = {"Sigma":sigma}
        theory = f"LoG = Laplacian(Gaussian(σ={sigma})). Smooth first to reduce noise sensitivity."
    op_name = detector

elif category == "Morphological Ops":
    op = st.selectbox("Operation",["Erosion","Dilation","Opening","Closing","Gradient","Top-Hat"])
    ksize = st.slider("SE size",3,31,7,step=2)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ksize,ksize))
    mmap = {"Erosion":cv2.MORPH_ERODE,"Dilation":cv2.MORPH_DILATE,
            "Opening":cv2.MORPH_OPEN,"Closing":cv2.MORPH_CLOSE,
            "Gradient":cv2.MORPH_GRADIENT,"Top-Hat":cv2.MORPH_TOPHAT}
    before = binary
    after  = cv2.morphologyEx(binary, mmap[op], kernel)
    params = {"SE size":f"{ksize}×{ksize}", "Shape":"Ellipse"}
    tmap   = {"Erosion":"Shrinks bright regions; removes protrusions smaller than SE.",
              "Dilation":"Expands bright regions; fills small gaps.",
              "Opening":"Erosion→Dilation: removes small bright noise.",
              "Closing":"Dilation→Erosion: fills small dark holes.",
              "Gradient":"Dilation−Erosion: extracts object boundary.",
              "Top-Hat":"Input−Opening: extracts small bright details."}
    theory  = tmap.get(op,"")
    op_name = op

elif category == "Colour Processing":
    before = img_rgb
    op = st.selectbox("Operation",["Greyscale","Channel separation (Red)","Pseudo-colour (Jet)","HSV — Hue channel"])
    if op == "Greyscale":
        after = gray; before = img_rgb
        theory = "Convert RGB → Greyscale using Y = 0.299R + 0.587G + 0.114B."
    elif op == "Channel separation (Red)":
        after = img_rgb[:,:,0]; before = img_rgb
        theory = "Isolate the Red channel — shows which regions have high R values."
    elif op == "Pseudo-colour (Jet)":
        pseudo = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        after  = cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB); before = gray
        theory = "Pseudo-colour maps each intensity to a colour via JET LUT — enhances visual discrimination."
    else:
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        after = hsv[:,:,0]; before = gray
        theory = "Hue channel: colour type regardless of brightness. Uniform for same-colour regions."
    op_name = op
    params  = {}

else:  # Intensity Transforms
    op = st.selectbox("Transform",["Gamma correction","Log transform","Histogram stretch","Thresholding"])
    if op == "Gamma correction":
        gamma = st.slider("γ", 0.1, 4.0, 1.5)
        lut   = np.array([((i/255.0)**gamma)*255 for i in range(256)], dtype=np.uint8)
        after  = cv2.LUT(gray, lut)
        params = {"Gamma":gamma}
        theory = f"I_out = I_in^{gamma:.2f}. γ<1 brightens (useful for dark images); γ>1 darkens."
    elif op == "Log transform":
        c = st.slider("c", 1, 50, 10)
        after  = normalize_display(c * np.log1p(gray.astype(float)))
        params = {"c":c}
        theory = f"I_out = {c}×log(1+I_in). Compresses high intensities, stretches low ones."
    elif op == "Histogram stretch":
        mn,mx = int(gray.min()), int(gray.max())
        after  = np.clip((gray.astype(float)-mn)/(mx-mn)*255,0,255).astype(np.uint8)
        params = {"Original min":mn, "Original max":mx}
        theory = "Linear stretch: maps [min,max] → [0,255]. Simple contrast enhancement."
    else:
        T = st.slider("Threshold T", 0, 255, 127)
        _, after = cv2.threshold(gray, T, 255, cv2.THRESH_BINARY)
        params  = {"Threshold T":T}
        theory  = f"Binary: pixel=255 if I>{T} else 0."
    op_name = op

# ── Render comparison ──────────────────────────────────────────────────────────
st.markdown(f"### 🔄 Comparing: **{op_name}**")

comparison_slider(before, after, label_before="Original", label_after=op_name, key=op_name)

st.markdown("---")
c1, c2, c3 = st.columns(3)
b_u8 = before.astype(np.uint8) if before.dtype != np.uint8 else before
a_u8 = after.astype(np.uint8)  if after.dtype  != np.uint8 else after
b_gray = b_u8 if len(b_u8.shape)==2 else cv2.cvtColor(b_u8, cv2.COLOR_RGB2GRAY)
a_gray = a_u8 if len(a_u8.shape)==2 else cv2.cvtColor(a_u8, cv2.COLOR_RGB2GRAY)
c1.metric("PSNR (vs original)", f"{psnr(b_gray, a_gray):.1f} dB")
c2.metric("Mean intensity (before)", f"{b_gray.mean():.1f}")
c3.metric("Mean intensity (after)",  f"{a_gray.mean():.1f}")

if theory:
    theory_box(theory)

if params:
    st.markdown("**Parameters used:**")
    param_cols = st.columns(len(params))
    for col,(k,v) in zip(param_cols, params.items()):
        col.metric(str(k), str(v))

# ── PDF export of this comparison ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📄 Add to Lab Report")
with st.expander("Export this comparison to PDF"):
    sname = st.text_input("Student name", "")
    rno   = st.text_input("Roll number", "")
    if st.button("Generate PDF"):
        b_img = b_gray if len(b_u8.shape)==2 else b_u8
        a_img = a_gray if len(a_u8.shape)==2 else a_u8
        ops = [{
            "title":      op_name,
            "theory":     theory,
            "parameters": params,
            "before_img": b_img,
            "after_img":  a_img,
            "metrics":    {
                "PSNR":       f"{psnr(b_gray,a_gray):.1f} dB",
                "Before mean":f"{b_gray.mean():.1f}",
                "After mean": f"{a_gray.mean():.1f}",
            }
        }]
        pdf_bytes = generate_pdf_report(ops, sname, rno, "DIP Comparison")
        if pdf_bytes:
            st.download_button("⬇ Download PDF", pdf_bytes,
                               f"lab_{op_name.replace(' ','_')}.pdf","application/pdf")
