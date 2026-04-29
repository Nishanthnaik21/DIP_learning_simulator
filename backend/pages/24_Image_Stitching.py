import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import numpy as np
import cv2
import io
from PIL import Image as PILImage
from utils.theme import inject, page_header, theory_card, metric_row, section_title
from utils.helpers import to_gray, fig_to_st
import matplotlib.pyplot as plt

inject("Image Stitching", "🔗")


page_header("Image Stitching — Panorama Builder",
            "FEATURE MATCHING · HOMOGRAPHY · RANSAC · PERSPECTIVE WARPING", "🔗", "#ffb700")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "Image stitching creates a panorama from overlapping images. Pipeline: "
    "(1) Detect ORB/SIFT features in each image. "
    "(2) Match features between adjacent images using BFMatcher. "
    "(3) Estimate homography H using RANSAC to filter outliers. "
    "(4) Warp one image into the coordinate space of the other using perspective transform. "
    "(5) Blend the overlapping region. "
    "Covers Module 5 (feature detection), Module 2 (frequency/spatial transforms)."
)

st.markdown("""
<div style="background:rgba(255,183,0,0.08);border:1px solid rgba(255,183,0,0.25);
            border-radius:10px;padding:12px 16px;margin-bottom:18px;font-size:0.84rem;color:#fde68a">
  📷 <b>Upload 2–3 overlapping images</b> of the same scene taken from slightly different angles.
  For best results: 30–50% overlap, same exposure, no moving objects.
</div>""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────
files = st.file_uploader("Upload 2–3 overlapping images", type=["jpg","jpeg","png"],
                          accept_multiple_files=True, key="stitch_files")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Stitching Settings")
n_features    = st.sidebar.slider("ORB keypoints", 200, 2000, 500)
match_ratio   = st.sidebar.slider("Lowe ratio test", 0.5, 0.9, 0.75)
ransac_thresh = st.sidebar.slider("RANSAC threshold", 1.0, 10.0, 4.0)
blend_mode    = st.sidebar.selectbox("Blending", ["Simple average","Maximum","Feather blend"])
show_matches  = st.sidebar.checkbox("Show feature matches", value=True)

if not files or len(files) < 2:
    st.markdown("""
    <div style="background:rgba(10,30,70,0.45);border:2px dashed rgba(255,183,0,0.3);
                border-radius:12px;padding:50px 20px;text-align:center">
      <div style="font-size:2.5rem;margin-bottom:10px">🖼️ + 🖼️</div>
      <div style="color:#3a6a9a;font-size:0.9rem">Upload at least 2 overlapping images to begin</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Load images ────────────────────────────────────────────────────────────────
images = []
for f in files[:3]:
    img = np.array(PILImage.open(f).convert("RGB"))
    # Resize if too large
    max_dim = 600
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w*scale), int(h*scale)))
    images.append(img)

section_title("INPUT IMAGES","#ffb700")
img_cols = st.columns(len(images))
for col, img in zip(img_cols, images):
    with col: st.image(img, use_container_width=True)

# ── Feature detection & matching ───────────────────────────────────────────────
section_title("FEATURE MATCHING","#ffb700")

def match_images(img1, img2, n_feat=500, ratio=0.75):
    """Find ORB features and match between two images."""
    g1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    g2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(nfeatures=n_feat)
    kp1, des1 = orb.detectAndCompute(g1, None)
    kp2, des2 = orb.detectAndCompute(g2, None)
    if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
        return None, None, None, kp1, kp2
    bf      = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.knnMatch(des1, des2, k=2)
    good    = [m for m,n in matches if len([m,n])==2 and m.distance < ratio * n.distance]
    return good, kp1, kp2, des1, des2

def compute_homography(kp1, kp2, good_matches, ransac_thr):
    """Compute homography using RANSAC."""
    if len(good_matches) < 4:
        return None, 0
    src = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
    dst = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, ransac_thr)
    inliers = int(mask.sum()) if mask is not None else 0
    return H, inliers

def stitch_two(img1, img2, H, blend):
    """Warp img1 into img2 space and blend."""
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    # Find output canvas size
    corners = np.float32([[0,0],[w1,0],[w1,h1],[0,h1]]).reshape(-1,1,2)
    warped_corners = cv2.perspectiveTransform(corners, H)
    all_corners = np.concatenate([
        warped_corners,
        np.float32([[0,0],[w2,0],[w2,h2],[0,h2]]).reshape(-1,1,2)
    ])
    x_min = int(np.floor(all_corners[:,:,0].min()))
    y_min = int(np.floor(all_corners[:,:,1].min()))
    x_max = int(np.ceil(all_corners[:,:,0].max()))
    y_max = int(np.ceil(all_corners[:,:,1].max()))
    canvas_w = min(x_max - x_min, 2400)
    canvas_h = min(y_max - y_min, 1800)
    # Offset transform
    T = np.array([[1,0,-x_min],[0,1,-y_min],[0,0,1]], dtype=np.float64)
    H_shifted = T @ H
    warped1 = cv2.warpPerspective(img1, H_shifted, (canvas_w, canvas_h))
    canvas  = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    # Place img2
    y_off = -y_min; x_off = -x_min
    y_off = max(0, min(y_off, canvas_h - h2))
    x_off = max(0, min(x_off, canvas_w - w2))
    canvas[y_off:y_off+h2, x_off:x_off+w2] = img2
    # Blend
    mask1 = (warped1.sum(axis=2) > 0).astype(np.uint8)
    mask2 = (canvas.sum(axis=2) > 0).astype(np.uint8)
    overlap = mask1 & mask2
    result  = canvas.copy()
    if blend == "Simple average":
        result[overlap==1] = ((warped1[overlap==1].astype(float) + canvas[overlap==1].astype(float))/2).astype(np.uint8)
        result[mask1==1]   = np.where((mask1==1)[:,:,None] & (mask2==0)[:,:,None], warped1, result)[mask1==1]
    elif blend == "Maximum":
        result = np.maximum(warped1, canvas)
    else:  # Feather
        dist1 = cv2.distanceTransform(mask1*255, cv2.DIST_L2, 5)
        dist2 = cv2.distanceTransform(mask2*255, cv2.DIST_L2, 5)
        w1_map = dist1 / (dist1 + dist2 + 1e-10)
        w2_map = 1 - w1_map
        for c in range(3):
            result[:,:,c] = np.clip(
                warped1[:,:,c].astype(float)*w1_map + canvas[:,:,c].astype(float)*w2_map, 0, 255
            ).astype(np.uint8)
    return result

# ── Run ─────────────────────────────────────────────────────────────────────
if st.button("🚀 Stitch Images"):
    with st.spinner("Detecting features and matching..."):
        result_img = images[0].copy()
        total_inliers = 0; total_matches = 0
        match_viz_list = []

        for i in range(len(images)-1):
            img_a = result_img; img_b = images[i+1]
            good, kp1, kp2, des1, des2 = match_images(img_a, img_b, n_features, match_ratio)
            if good is None or len(good) < 4:
                st.warning(f"Not enough matches between image {i+1} and {i+2}. Try more overlap.")
                continue
            total_matches += len(good)
            H, inliers = compute_homography(kp1, kp2, good, ransac_thresh)
            total_inliers += inliers
            if H is None:
                st.warning(f"Could not compute homography for pair {i+1}–{i+2}."); continue
            if show_matches:
                n_show = min(30, len(good))
                img_match = cv2.drawMatches(
                    cv2.cvtColor(img_a, cv2.COLOR_RGB2GRAY), kp1,
                    cv2.cvtColor(img_b, cv2.COLOR_RGB2GRAY), kp2,
                    good[:n_show], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
                )
                match_viz_list.append((img_match, f"Matches: {len(good)} good, {inliers} inliers"))
            result_img = stitch_two(img_a, img_b, H, blend_mode)

    if show_matches and match_viz_list:
        for mv, mv_label in match_viz_list:
            st.markdown(f"**{mv_label}**")
            st.image(cv2.cvtColor(mv, cv2.COLOR_BGR2RGB), use_container_width=True)

    section_title("PANORAMA RESULT","#ffb700")
    st.image(result_img, caption=f"Stitched panorama ({result_img.shape[1]}×{result_img.shape[0]})",
             use_container_width=True)

    metric_row([
        ("Output size",    f"{result_img.shape[1]}×{result_img.shape[0]}"),
        ("Images stitched",str(len(images))),
        ("Total matches",  str(total_matches)),
        ("RANSAC inliers", str(total_inliers)),
        ("Blend mode",     blend_mode.split()[0]),
    ])

    # Download
    pil_out = PILImage.fromarray(result_img)
    buf     = io.BytesIO(); pil_out.save(buf,"PNG"); buf.seek(0)
    st.download_button("⬇ Download panorama (PNG)", buf, "panorama.png","image/png")

    theory_card(
        f"ORB detected features in each image pair. Brute-force matching with ratio test "
        f"(threshold={match_ratio}) filtered good matches. RANSAC (threshold={ransac_thresh}px) "
        f"estimated the homography matrix H from matched keypoints. "
        f"Homography warps one image into the coordinate space of the other. "
        f"Blending mode: {blend_mode}."
    )
else:
    section_title("PIPELINE OVERVIEW","#ffb700")
    for i, (step, desc) in enumerate([
        ("Feature Detection", "ORB detects keypoints in each image"),
        ("Feature Matching",  "BFMatcher + Lowe ratio test filters good matches"),
        ("Homography",        "RANSAC estimates perspective transform H"),
        ("Warping",           "cv2.warpPerspective applies H to image"),
        ("Blending",          "Overlap region blended using selected mode"),
    ], 1):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                    border-bottom:1px solid rgba(255,183,0,0.1)">
          <div style="width:28px;height:28px;background:rgba(255,183,0,0.15);border:1px solid rgba(255,183,0,0.3);
                      border-radius:50%;display:flex;align-items:center;justify-content:center;
                      font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#ffb700;flex-shrink:0">{i}</div>
          <div>
            <span style="font-weight:600;color:#ffb700">{step}</span>
            <span style="color:#3a6a9a;font-size:0.83rem"> — {desc}</span>
          </div>
        </div>""", unsafe_allow_html=True)
