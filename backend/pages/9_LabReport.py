import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
from utils.helpers import *



st.set_page_config(page_title="Lab Report Generator", page_icon="📄", layout="wide")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj

st.markdown("## 📄 PDF Lab Report Generator")
st.caption("Build a complete, formatted lab record for submission — add operations, images, and parameters")
st.markdown("---")

img_rgb = upload_image("pdf_upload")
gray    = to_gray(img_rgb)

# ── Student details ────────────────────────────────────────────────────────────
st.markdown("### 👤 Student Details")
c1, c2, c3 = st.columns(3)
student_name = c1.text_input("Student Name", "")
roll_no      = c2.text_input("Roll Number", "")
module_name  = c3.selectbox("Module", [
    "Module 1 — Digital Image Fundamentals",
    "Module 2 — Spatial & Frequency Domain",
    "Module 3 — Image Restoration",
    "Module 4 — Color, Wavelets & Morphology",
    "Module 5 — Image Segmentation",
    "All Modules — Full Lab Record",
])

st.markdown("---")

# ── Session state for operations list ─────────────────────────────────────────
if "pdf_ops" not in st.session_state:
    st.session_state["pdf_ops"] = []

# ── Add an operation ───────────────────────────────────────────────────────────
st.markdown("### ➕ Add Operations to Report")
with st.expander("Add a new operation", expanded=True):
    op_title = st.selectbox("Operation", [
        "Histogram Equalisation", "CLAHE (Adaptive)", "Gaussian Blur",
        "Median Filter", "Canny Edge Detection", "Sobel Edge Detection",
        "Morphological Erosion", "Morphological Dilation", "Morphological Opening",
        "Morphological Closing", "Otsu Thresholding", "Adaptive Thresholding",
        "Gamma Correction", "Laplacian Sharpening", "DFT — Low Pass Filter",
        "DFT — High Pass Filter", "Wiener Restoration (simulated)", "Pseudo-Colour (Jet)",
        "Harris Corner Detection", "Hough Circle Transform",
    ])

    # Dynamic parameters based on operation
    params = {}
    before = gray.copy()
    after  = gray.copy()

    if op_title == "Histogram Equalisation":
        after = cv2.equalizeHist(gray)
        theory = "HE redistributes pixel intensities so the cumulative histogram is approximately linear — maximises contrast."
    elif op_title == "CLAHE (Adaptive)":
        clip = st.slider("Clip limit", 1.0, 10.0, 2.0, key="pdf_clip")
        tile = st.slider("Tile size", 2, 16, 8, key="pdf_tile")
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile,tile))
        after = clahe.apply(gray); params={"Clip":clip,"Tile":f"{tile}×{tile}"}
        theory = f"CLAHE: local contrast enhancement in {tile}×{tile} tiles. Clip limit {clip} prevents noise amplification."
    elif op_title == "Gaussian Blur":
        k = st.slider("Kernel",3,31,9,2,key="pdf_gk"); s = st.slider("Sigma",0.5,8.0,2.0,key="pdf_gs")
        after = cv2.GaussianBlur(gray,(k,k),s); params={"Kernel":f"{k}×{k}","Sigma":s}
        theory = f"Gaussian blur G(x,y)=e^(-(x²+y²)/2σ²)/(2πσ²). σ={s} controls spread."
    elif op_title == "Median Filter":
        k = st.slider("Kernel",3,21,7,2,key="pdf_mk")
        after = cv2.medianBlur(gray,k); params={"Kernel":f"{k}×{k}"}
        theory = "Median filter: each pixel = median of neighbourhood. Removes salt-and-pepper noise, preserves edges."
    elif op_title == "Canny Edge Detection":
        t1=st.slider("Low T",10,200,50,key="pdf_ct1"); t2=st.slider("High T",50,400,150,key="pdf_ct2")
        after = cv2.Canny(gray,t1,t2); params={"Low threshold":t1,"High threshold":t2}
        theory = f"Canny: Gaussian smooth → Sobel gradient → NMS → double threshold [{t1},{t2}] → hysteresis tracking."
    elif op_title == "Sobel Edge Detection":
        sx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3); sy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)
        after = cv2.convertScaleAbs(np.sqrt(sx**2+sy**2)); params={"Kernel":"3×3"}
        theory = "Sobel: gradient magnitude √(Gx²+Gy²). Gx detects vertical edges, Gy detects horizontal edges."
    elif op_title in ("Morphological Erosion","Morphological Dilation","Morphological Opening","Morphological Closing"):
        k=st.slider("SE size",3,31,9,2,key="pdf_mk2")
        _,bin_img = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k))
        before = bin_img
        mmap={"Morphological Erosion":cv2.MORPH_ERODE,"Morphological Dilation":cv2.MORPH_DILATE,
              "Morphological Opening":cv2.MORPH_OPEN,"Morphological Closing":cv2.MORPH_CLOSE}
        after=cv2.morphologyEx(bin_img,mmap[op_title],kernel); params={"SE size":f"{k}×{k}"}
        tmap={"Morphological Erosion":"Erosion shrinks bright regions — removes protrusions smaller than SE.",
              "Morphological Dilation":"Dilation expands bright regions — fills small gaps within objects.",
              "Morphological Opening":"Opening = Erosion then Dilation. Removes small bright noise.",
              "Morphological Closing":"Closing = Dilation then Erosion. Fills small dark holes."}
        theory=tmap[op_title]
    elif op_title == "Otsu Thresholding":
        T,after = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        params={"Auto threshold T":int(T)}
        theory = f"Otsu: automatically finds optimal T={int(T)} by minimising weighted intra-class variance."
    elif op_title == "Adaptive Thresholding":
        block=st.slider("Block size",3,99,11,2,key="pdf_ablock"); C=st.slider("C",-30,30,2,key="pdf_aC")
        after=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,block,C)
        params={"Block":block,"C":C}
        theory = f"Adaptive threshold: each pixel's T = Gaussian mean of {block}×{block} neighbourhood - {C}."
    elif op_title == "Gamma Correction":
        gamma=st.slider("Gamma γ",0.1,4.0,1.5,key="pdf_gamma")
        lut=np.array([((i/255.0)**gamma)*255 for i in range(256)],dtype=np.uint8)
        after=cv2.LUT(gray,lut); params={"Gamma γ":gamma}
        theory = f"I_out = I_in^{gamma:.2f}. γ<1 brightens (maps darks higher); γ>1 darkens."
    elif op_title == "Laplacian Sharpening":
        w=st.slider("Weight",0.1,2.0,1.0,key="pdf_lapw")
        lap=cv2.Laplacian(gray.astype(np.float32),cv2.CV_32F)
        after=np.clip(gray.astype(float)-w*lap,0,255).astype(np.uint8); params={"Weight":w}
        theory = f"Sharpened = Original - {w}×Laplacian. Laplacian ∇²f detects rapid intensity changes."
    elif op_title in ("DFT — Low Pass Filter","DFT — High Pass Filter"):
        D0=st.slider("Cut-off D₀",5,80,30,key="pdf_D0")
        rows,cols=gray.shape; crow,ccol=rows//2,cols//2
        Y,X=np.ogrid[:rows,:cols]; D=np.sqrt((Y-crow)**2+(X-ccol)**2)
        H=np.exp(-(D**2)/(2*D0**2))
        if "High" in op_title: H=1-H
        F=np.fft.fftshift(np.fft.fft2(gray.astype(float)))
        after=normalize_display(np.abs(np.fft.ifft2(np.fft.ifftshift(F*H))))
        params={"D₀":D0,"Type":"Gaussian"}
        theory=f"{'Low-pass' if 'Low' in op_title else 'High-pass'} Gaussian filter in frequency domain. D₀={D0} controls cutoff."
    elif op_title == "Wiener Restoration (simulated)":
        K=st.slider("K",0.001,0.3,0.01,format="%.3f",key="pdf_K")
        sigma_n=st.slider("Noise σ",5,40,15,key="pdf_sn")
        psf=np.zeros_like(gray.astype(float)); psf[gray.shape[0]//2,:10]=1/10
        H2=np.fft.fft2(psf)
        G=H2*np.fft.fft2(gray.astype(float))+np.fft.fft2(np.random.normal(0,sigma_n,gray.shape))
        Hw=np.conj(H2)/(np.abs(H2)**2+K)
        after=normalize_display(np.abs(np.fft.ifft2(Hw*G))); params={"K":K,"Noise σ":sigma_n}
        theory = f"Wiener: Ĥ=H*/(|H|²+K). K={K:.3f}. Lower K → closer to inverse filter; higher K → more regularisation."
    elif op_title == "Pseudo-Colour (Jet)":
        before=img_rgb
        pseudo=cv2.applyColorMap(gray,cv2.COLORMAP_JET)
        after=cv2.cvtColor(pseudo,cv2.COLOR_BGR2RGB); params={"Colormap":"JET"}
        theory = "Pseudo-colour maps intensity values to colours via a LUT. Enhances visual discrimination; adds no real colour info."
    elif op_title == "Harris Corner Detection":
        dst=cv2.cornerHarris(gray,2,3,0.04); dst=cv2.dilate(dst,None)
        overlay=cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
        overlay[dst>0.01*dst.max()]=[255,0,0]
        after=overlay; params={"k":0.04,"Block":2}
        theory = "Harris R=det(M)-k·trace(M)². Large positive R=corner (marked red). Large negative R=edge."
    elif op_title == "Hough Circle Transform":
        circles=cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1.5,30,param1=80,param2=30,minRadius=10,maxRadius=60)
        overlay=cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
        if circles is not None:
            for (x,y,r) in np.round(circles[0]).astype(int):
                cv2.circle(overlay,(x,y),r,(0,200,255),2); cv2.circle(overlay,(x,y),2,(255,100,0),3)
        after=overlay; params={"dp":1.5,"minDist":30,"minR":10,"maxR":60}
        theory = "Circular Hough: each edge pixel votes in (cx,cy,r) space. Peaks = detected circles."
    else:
        theory = "Standard DIP operation."

    # Preview
    col1,col2 = st.columns(2)
    with col1: st.markdown("**Before**"); st.image(before, use_container_width=True, clamp=True)
    with col2: st.markdown("**After**");  st.image(after,  use_container_width=True, clamp=True)

    b_u8 = np.clip(before,0,255).astype(np.uint8)
    a_u8 = np.clip(after, 0,255).astype(np.uint8)
    bg = b_u8 if len(b_u8.shape)==2 else cv2.cvtColor(b_u8,cv2.COLOR_RGB2GRAY)
    ag = a_u8 if len(a_u8.shape)==2 else cv2.cvtColor(a_u8,cv2.COLOR_RGB2GRAY)
    st.metric("PSNR", f"{psnr(bg,ag):.1f} dB")

    if st.button("➕ Add this operation to report"):
        st.session_state["pdf_ops"].append({
            "title":      op_title,
            "theory":     theory,
            "parameters": params,
            "before_img": b_u8,
            "after_img":  a_u8,
            "metrics":    {
                "PSNR":            f"{psnr(bg,ag):.1f} dB",
                "Mean (before)":   f"{bg.mean():.1f}",
                "Mean (after)":    f"{ag.mean():.1f}",
                "Std (before)":    f"{bg.std():.1f}",
                "Std (after)":     f"{ag.std():.1f}",
            }
        })
        st.success(f"✅ '{op_title}' added to report. Total: {len(st.session_state['pdf_ops'])} operations.")
        st.rerun()

# ── Operations queue ───────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"### 📋 Report Queue — {len(st.session_state['pdf_ops'])} operation(s)")
if st.session_state["pdf_ops"]:
    for i, op in enumerate(st.session_state["pdf_ops"]):
        colA, colB = st.columns([6,1])
        colA.markdown(f"**{i+1}.** {op['title']} &nbsp;&nbsp; `PSNR: {op['metrics'].get('PSNR','—')}`")
        if colB.button("🗑️", key=f"del_{i}"):
            st.session_state["pdf_ops"].pop(i); st.rerun()
    if st.button("🗑️ Clear all"):
        st.session_state["pdf_ops"] = []; st.rerun()
else:
    st.info("No operations added yet. Use the panel above to add operations.")

# ── Generate PDF ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📥 Generate & Download PDF")
if st.session_state["pdf_ops"]:
    if st.button("🖨️ Generate PDF Lab Record", type="primary"):
        with st.spinner("Generating PDF..."):
            pdf_bytes = generate_pdf_report(
                st.session_state["pdf_ops"],
                student_name, roll_no, module_name
            )
        if pdf_bytes:
            fname = f"DIP_Lab_Record_{roll_no or 'student'}_{datetime.now().strftime('%Y%m%d')}.pdf"
            st.download_button("⬇ Download PDF", pdf_bytes, fname, "application/pdf")
            st.success(f"✅ PDF generated with {len(st.session_state['pdf_ops'])} experiments!")
        else:
            st.error("PDF generation failed — check reportlab installation.")
else:
    st.info("Add at least one operation above before generating the report.")

from datetime import datetime
