import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import io
from PIL import Image as PILImage
from utils.theme import inject, page_header, theory_card, metric_row, section_title
from utils.helpers import upload_image, to_gray, fig_to_st, normalize_display

inject("Template Matching", "🔍")


page_header("Template Matching",
            "CROSS-CORRELATION · 6 METHODS · HEATMAP · MULTI-SCALE SEARCH", "🔍", "#00a8ff")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "Template matching slides a small template image across a larger source image and computes "
    "a similarity score at every position. The result is a correlation map where peaks indicate "
    "probable match locations. Methods: TM_CCOEFF_NORMED (best for textured templates), "
    "TM_CCORR_NORMED (cross-correlation), TM_SQDIFF (sum of squared differences — lower=better). "
    "Multi-scale matching handles size variations by searching at multiple pyramid scales."
)

img_rgb = upload_image("tmpl_up")
gray    = to_gray(img_rgb)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Template Settings")
method_name = st.sidebar.selectbox("Matching method", [
    "TM_CCOEFF_NORMED (recommended)","TM_CCORR_NORMED","TM_SQDIFF_NORMED",
    "TM_CCOEFF","TM_CCORR","TM_SQDIFF"
])
multi_match    = st.sidebar.checkbox("Find multiple matches", value=True)
threshold      = st.sidebar.slider("Match threshold", 0.5, 0.99, 0.75)
multi_scale    = st.sidebar.checkbox("Multi-scale search", value=False)
show_heatmap   = st.sidebar.checkbox("Show correlation heatmap", value=True)

METHOD_MAP = {
    "TM_CCOEFF_NORMED (recommended)": cv2.TM_CCOEFF_NORMED,
    "TM_CCORR_NORMED": cv2.TM_CCORR_NORMED,
    "TM_SQDIFF_NORMED": cv2.TM_SQDIFF_NORMED,
    "TM_CCOEFF": cv2.TM_CCOEFF,
    "TM_CCORR":  cv2.TM_CCORR,
    "TM_SQDIFF": cv2.TM_SQDIFF,
}
method = METHOD_MAP[method_name]
is_sqdiff = "SQDIFF" in method_name

# ── Template selection ─────────────────────────────────────────────────────────
section_title("TEMPLATE SELECTION","#00a8ff")
tab_sel = st.tabs(["📦 Crop from image","📁 Upload template","✏️ Draw region"])

with tab_sel[0]:
    st.info("Specify crop coordinates (x1,y1) to (x2,y2) as percentage of image size")
    h, w = gray.shape
    c1,c2,c3,c4 = st.columns(4)
    x1_pct = c1.slider("x1 %", 0, 90, 20)
    y1_pct = c2.slider("y1 %", 0, 90, 20)
    x2_pct = c3.slider("x2 %", x1_pct+5, 100, min(x1_pct+25, 95))
    y2_pct = c4.slider("y2 %", y1_pct+5, 100, min(y1_pct+25, 95))
    x1,y1 = int(x1_pct/100*w), int(y1_pct/100*h)
    x2,y2 = int(x2_pct/100*w), int(y2_pct/100*h)
    template = gray[y1:y2, x1:x2]
    # Show selection
    preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    cv2.rectangle(preview, (x1,y1),(x2,y2),(0,200,255),2)
    col_p, col_t = st.columns(2)
    with col_p: st.image(preview, caption="Source with template region (cyan)", use_container_width=True)
    with col_t: st.image(template, caption=f"Template ({template.shape[1]}×{template.shape[0]})", use_container_width=True, clamp=True)

with tab_sel[1]:
    file_tmpl = st.file_uploader("Upload template image", type=["jpg","jpeg","png"], key="tmpl_file")
    if file_tmpl:
        template = np.array(PILImage.open(file_tmpl).convert("L"))
        st.image(template, caption=f"Template ({template.shape[1]}×{template.shape[0]})", use_container_width=False, width=200, clamp=True)

with tab_sel[2]:
    st.info("Draw template: specify pixel bounding box manually")
    hh, ww = gray.shape
    px1 = st.number_input("x1", 0, ww-1, ww//4)
    py1 = st.number_input("y1", 0, hh-1, hh//4)
    px2 = st.number_input("x2", 1, ww, ww*3//4)
    py2 = st.number_input("y2", 1, hh, hh*3//4)
    template = gray[int(py1):int(py2), int(px1):int(px2)]

# ── Run matching ───────────────────────────────────────────────────────────────
if template.size == 0:
    st.warning("Template is empty. Adjust the crop region."); st.stop()
if template.shape[0] > gray.shape[0] or template.shape[1] > gray.shape[1]:
    st.warning("Template is larger than source image."); st.stop()

section_title("MATCHING RESULTS","#00fff5")

def run_matching(src, tmpl, method, threshold, multi, is_sqdiff, scales=None):
    """Run template matching, optionally multi-scale."""
    best_val = -np.inf if not is_sqdiff else np.inf
    best_result = None; best_scale = 1.0
    search_scales = scales if scales else [1.0]
    for scale in search_scales:
        if scale != 1.0:
            sw = max(1, int(src.shape[1]*scale)); sh = max(1, int(src.shape[0]*scale))
            src_s = cv2.resize(src,(sw,sh))
        else:
            src_s = src
        if tmpl.shape[0] > src_s.shape[0] or tmpl.shape[1] > src_s.shape[1]: continue
        result = cv2.matchTemplate(src_s.astype(np.uint8), tmpl.astype(np.uint8), method)
        if is_sqdiff:
            mn, mx, mn_loc, mx_loc = cv2.minMaxLoc(result)
            val = mn
            if val < best_val: best_val=val; best_result=result; best_scale=scale
        else:
            mn, mx, mn_loc, mx_loc = cv2.minMaxLoc(result)
            val = mx
            if val > best_val: best_val=val; best_result=result; best_scale=scale
    return best_result, best_scale

scales = np.linspace(0.5, 1.5, 7) if multi_scale else [1.0]
result_map, best_scale = run_matching(gray, template, method, threshold, multi_match, is_sqdiff, scales)

# Normalise result for display
result_norm = cv2.normalize(result_map, None, 0, 1, cv2.NORM_MINMAX)

# Find matches
overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
th, tw  = template.shape[:2]
locations = []

if multi_match:
    if is_sqdiff:
        match_mask = (result_norm <= 1-threshold).astype(np.uint8)
    else:
        match_mask = (result_norm >= threshold).astype(np.uint8)
    # Non-maximum suppression using dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (tw//2, th//2))
    dilated = cv2.dilate(result_map if not is_sqdiff else -result_map, kernel)
    local_max = (result_map if not is_sqdiff else -result_map) >= dilated - 1e-6
    combined  = match_mask & local_max.astype(np.uint8)
    ys, xs = np.where(combined)
    for x, y in zip(xs[:50], ys[:50]):
        conf = float(result_norm[y,x])
        locations.append((x,y,conf))
        cv2.rectangle(overlay,(x,y),(x+tw,y+th),(0,200,255),2)
        cv2.putText(overlay,f"{conf:.2f}",(x,y-4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,200,0),1)
else:
    if is_sqdiff:
        mn,mx,mn_loc,_ = cv2.minMaxLoc(result_map)
        best_loc = mn_loc; conf = 1-float(result_norm[mn_loc[1],mn_loc[0]])
    else:
        mn,mx,_,mx_loc = cv2.minMaxLoc(result_map)
        best_loc = mx_loc; conf = float(result_norm[mx_loc[1],mx_loc[0]])
    locations = [(*best_loc, conf)]
    cv2.rectangle(overlay,best_loc,(best_loc[0]+tw,best_loc[1]+th),(0,200,255),2)

# ── Display ────────────────────────────────────────────────────────────────────
if show_heatmap:
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown("**Source image**"); st.image(gray, use_container_width=True, clamp=True)
    with c2: st.markdown(f"**{len(locations)} match(es) found**"); st.image(overlay, use_container_width=True)
    with c3:
        st.markdown("**Correlation heatmap**")
        heatmap = cv2.applyColorMap((result_norm*255).astype(np.uint8), cv2.COLORMAP_HOT)
        st.image(cv2.cvtColor(heatmap,cv2.COLOR_BGR2RGB), use_container_width=True)
else:
    c1,c2 = st.columns(2)
    with c1: st.image(gray, caption="Source", use_container_width=True, clamp=True)
    with c2: st.image(overlay, caption=f"{len(locations)} matches", use_container_width=True)

# Metrics
metric_row([
    ("Matches found",   str(len(locations))),
    ("Best confidence", f"{max([l[2] for l in locations],default=0):.3f}" if locations else "—"),
    ("Method",          method_name.split("(")[0].strip()),
    ("Template size",   f"{tw}×{th}"),
    ("Search scale",    f"{best_scale:.2f}×" if multi_scale else "1.0×"),
])

theory_card(
    f"Method: {method_name}. Correlation map size = (H-h+1)×(W-w+1) = "
    f"({gray.shape[0]}-{th}+1)×({gray.shape[1]}-{tw}+1) = "
    f"{gray.shape[0]-th+1}×{gray.shape[1]-tw+1}. "
    f"Found {len(locations)} match(es) above threshold {threshold}."
)
