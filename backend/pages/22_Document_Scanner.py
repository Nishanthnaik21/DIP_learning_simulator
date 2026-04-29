import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import numpy as np
import cv2
import io
from PIL import Image as PILImage
from utils.theme import inject, page_header, theory_card, metric_row, section_title
from utils.helpers import upload_image, to_gray, comparison_slider

inject("Document Scanner", "📄")


page_header("Document Scanner",
            "CORNER DETECTION · PERSPECTIVE TRANSFORM · ADAPTIVE THRESHOLD · CLEAN SCAN", "📄", "#00fff5")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "A document scanner pipeline: (1) Detect edges using Canny. (2) Find the largest quadrilateral "
    "contour in the edge map — this is the document boundary. (3) Identify the 4 corner points of "
    "the document. (4) Apply perspective transform (homography) to obtain a top-down 'bird's eye' "
    "view. (5) Enhance with adaptive thresholding to produce a clean black-and-white scan. "
    "Covers Module 2 (filtering), Module 4 (morphology), Module 5 (corner detection + contours)."
)

img_rgb = upload_image("scan_up")
gray    = to_gray(img_rgb)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📄 Scanner Settings")
edge_low   = st.sidebar.slider("Canny low threshold",  10, 100, 30)
edge_high  = st.sidebar.slider("Canny high threshold", 50, 300, 100)
blur_k     = st.sidebar.slider("Pre-blur kernel", 1, 11, 5, step=2)
morph_k    = st.sidebar.slider("Morph close kernel", 1, 15, 5, step=2)
output_w   = st.sidebar.slider("Output width (px)", 300, 1200, 600, step=50)
output_h   = st.sidebar.slider("Output height (px)", 400, 1600, 800, step=50)
enhance    = st.sidebar.selectbox("Enhancement", ["Adaptive Threshold","CLAHE","Greyscale only","Otsu"])
auto_detect = st.sidebar.checkbox("Auto-detect document corners", value=True)

# ── Corner detection ──────────────────────────────────────────────────────────
def order_points(pts):
    """Order: TL, TR, BR, BL."""
    rect = np.zeros((4,2), dtype=np.float32)
    s = pts.sum(axis=1); diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]   # TL
    rect[2] = pts[np.argmax(s)]   # BR
    rect[1] = pts[np.argmin(diff)]# TR
    rect[3] = pts[np.argmax(diff)]# BL
    return rect

def find_doc_corners(gray, low, high, bk, mk):
    """Find 4 corners of document in image."""
    blurred = cv2.GaussianBlur(gray, (bk, bk), 0)
    edges   = cv2.Canny(blurred, low, high)
    kernel  = cv2.getStructuringElement(cv2.MORPH_RECT, (mk, mk))
    closed  = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours    = sorted(contours, key=cv2.contourArea, reverse=True)
    for cnt in contours[:10]:
        peri  = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
        if len(approx) == 4:
            return approx.reshape(4,2).astype(np.float32), edges, closed
    # Fallback: use image corners
    h, w = gray.shape
    corners = np.array([[w*0.1,h*0.1],[w*0.9,h*0.1],[w*0.9,h*0.9],[w*0.1,h*0.9]], dtype=np.float32)
    return corners, edges, closed

corners, edges, morphed = find_doc_corners(gray, edge_low, edge_high, blur_k, morph_k)
ordered = order_points(corners)

# ── Manual corner adjustment ──────────────────────────────────────────────────
if not auto_detect:
    section_title("MANUAL CORNER ADJUSTMENT","#00fff5")
    st.info("Drag sliders to manually set document corners (as % of image dimensions)")
    h_img, w_img = gray.shape
    c_cols = st.columns(4)
    labels = ["Top-Left","Top-Right","Bottom-Right","Bottom-Left"]
    manual_corners = []
    for ci, (c_col, lbl) in enumerate(zip(c_cols, labels)):
        with c_col:
            st.markdown(f"**{lbl}**")
            default_x = float(ordered[ci][0])/w_img*100
            default_y = float(ordered[ci][1])/h_img*100
            cx = st.slider(f"X%", 0.0, 100.0, float(default_x), key=f"cx{ci}")
            cy = st.slider(f"Y%", 0.0, 100.0, float(default_y), key=f"cy{ci}")
            manual_corners.append([cx/100*w_img, cy/100*h_img])
    ordered = np.array(manual_corners, dtype=np.float32)

# ── Perspective transform ──────────────────────────────────────────────────────
dst_pts = np.array([[0,0],[output_w-1,0],[output_w-1,output_h-1],[0,output_h-1]], dtype=np.float32)
M       = cv2.getPerspectiveTransform(ordered, dst_pts)
warped  = cv2.warpPerspective(gray, M, (output_w, output_h))

# ── Enhancement ───────────────────────────────────────────────────────────────
if enhance == "Adaptive Threshold":
    block = st.sidebar.slider("Adaptive block size", 5, 51, 11, step=2)
    C_val = st.sidebar.slider("C constant", -20, 20, 5)
    enhanced = cv2.adaptiveThreshold(warped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, block, C_val)
elif enhance == "CLAHE":
    clahe    = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(warped)
elif enhance == "Otsu":
    _, enhanced = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
else:
    enhanced = warped

# ── Draw corners ───────────────────────────────────────────────────────────────
preview = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR).copy()
if len(preview.shape) == 2:
    preview = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR)
else:
    preview = img_rgb.copy()

h_full, w_full = img_rgb.shape[:2]
scale_x = w_full / gray.shape[1]
scale_y = h_full / gray.shape[0]
corners_full = ordered.copy()
corners_full[:,0] *= scale_x; corners_full[:,1] *= scale_y

pts_int = corners_full.astype(int)
cv2.polylines(preview, [pts_int], True, (0,220,255), 3)
corner_colors = [(0,200,255),(255,150,0),(255,50,50),(100,255,100)]
corner_labels = ["TL","TR","BR","BL"]
for i, (pt, clr, lbl) in enumerate(zip(pts_int, corner_colors, corner_labels)):
    cv2.circle(preview, tuple(pt), 10, clr, -1)
    cv2.putText(preview, lbl, (pt[0]+12, pt[1]+6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, clr, 2)

# ── Display ─────────────────────────────────────────────────────────────────
section_title("SCAN PIPELINE","#00fff5")
tab1, tab2, tab3 = st.tabs(["🔍 DETECTION","📐 TRANSFORM","🔬 PIPELINE STEPS"])

with tab1:
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown("**Original + detected corners**"); st.image(preview, use_container_width=True)
    with c2: st.markdown("**Edge map (Canny)**"); st.image(edges, use_container_width=True, clamp=True)
    with c3: st.markdown("**Morphological close**"); st.image(morphed, use_container_width=True, clamp=True)

with tab2:
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("**Perspective corrected**")
        st.image(warped, use_container_width=True, clamp=True)
    with c2:
        st.markdown(f"**Final scan ({enhance})**")
        st.image(enhanced, use_container_width=True, clamp=True)
    st.markdown("#### ↔️ Compare original vs scan")
    comparison_slider(gray, enhanced, "Original", "Scanned", key="scan_cmp")

    # Download
    pil_out = PILImage.fromarray(enhanced)
    buf     = io.BytesIO(); pil_out.save(buf, "PNG"); buf.seek(0)
    st.download_button("⬇ Download scanned document (PNG)", buf, "scanned_document.png","image/png")
    metric_row([
        ("Output size",   f"{output_w}×{output_h}"),
        ("Enhancement",   enhance.split()[0]),
        ("Corners found", "4 (auto)" if auto_detect else "4 (manual)"),
    ])

with tab3:
    steps_html = [
        ("Step 1","Gaussian Blur","Reduce noise before edge detection","Kernel size × kernel size",f"cv2.GaussianBlur(gray, ({blur_k},{blur_k}), 0)"),
        ("Step 2","Canny Edge Detection","Detect document boundary edges","Low T / High T",f"cv2.Canny(blurred, {edge_low}, {edge_high})"),
        ("Step 3","Morphological Close","Connect broken edge segments","Kernel size",f"cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_{morph_k}x{morph_k})"),
        ("Step 4","Contour Detection","Find largest quadrilateral contour","—","cv2.findContours(closed, cv2.RETR_EXTERNAL, ...)"),
        ("Step 5","approxPolyDP","Approximate contour to 4 corners","epsilon=0.02×perimeter","cv2.approxPolyDP(cnt, 0.02*peri, True)"),
        ("Step 6","Perspective Transform","Warp document to top-down view",f"{output_w}×{output_h}",f"cv2.getPerspectiveTransform(src_pts, dst_pts)"),
        ("Step 7",enhance,"Enhance scanned text","Block/clip","cv2.adaptiveThreshold(...) or CLAHE or Otsu"),
    ]
    for snum, sname, sdesc, sparam, scode in steps_html:
        st.markdown(f"""
        <div style="background:rgba(10,30,70,0.45);border-left:3px solid #00fff5;
                    border-radius:0 10px 10px 0;padding:12px 16px;margin:8px 0;
                    display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap">
          <div style="min-width:60px;text-align:center">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#3a6a9a">{snum}</div>
            <div style="font-family:'Orbitron',monospace;font-size:0.72rem;color:#00fff5;font-weight:700">{sname}</div>
          </div>
          <div style="flex:1">
            <div style="font-size:0.82rem;color:#8ab4d4;margin-bottom:4px">{sdesc} — <span style="color:#3a6a9a">{sparam}</span></div>
            <code style="font-size:0.73rem;color:#7dd3fc;background:rgba(0,0,0,0.3);
                         padding:2px 6px;border-radius:4px">{scode}</code>
          </div>
        </div>""", unsafe_allow_html=True)
