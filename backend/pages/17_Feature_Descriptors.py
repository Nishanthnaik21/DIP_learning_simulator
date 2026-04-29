import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import io
from utils.theme import inject, page_header, theory_card, metric_row, code_card
from utils.helpers import upload_image, to_gray, fig_to_st

inject("Feature Descriptors", "📐")


page_header("Feature Descriptors",
            "SIFT KEYPOINTS · HOG VISUALISATION · ORB MATCHING · HISTOGRAM OF GRADIENTS", "📐", "#a855f7")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


img_rgb = upload_image("feat_up")
gray    = to_gray(img_rgb)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔑 SIFT Keypoints",
    "📊 HOG Features",
    "🔗 ORB Matching",
    "🌀 Gradient Analysis",
])

# ── TAB 1: SIFT ────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### SIFT — Scale-Invariant Feature Transform")
    theory_card(
        "SIFT detects keypoints that are invariant to scale and rotation. "
        "For each keypoint it computes a 128-dimensional descriptor using gradient histograms "
        "in a 16×16 neighbourhood divided into 4×4 cells, each with 8 orientation bins. "
        "SIFT is robust to illumination changes, scale, and rotation — used in image matching and stitching."
    )
    n_features = st.slider("Max keypoints", 50, 1000, 300)
    try:
        sift = cv2.SIFT_create(nfeatures=n_features)
        kps, descs = sift.detectAndCompute(gray, None)
        annotated   = cv2.drawKeypoints(gray, kps, None,
                                         flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original**"); st.image(gray, use_container_width=True, clamp=True)
        with c2:
            st.markdown(f"**SIFT — {len(kps)} keypoints**")
            st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)

        metric_row([
            ("Keypoints found", len(kps)),
            ("Descriptor dim",  128),
            ("Descriptor shape", str(descs.shape) if descs is not None else "None"),
        ])

        if kps and st.checkbox("Show keypoint statistics"):
            sizes     = [kp.size for kp in kps]
            responses = [kp.response for kp in kps]
            fig, axes = plt.subplots(1, 2, figsize=(10,3), facecolor="#0b0f1a")
            for ax in axes: ax.set_facecolor("#1a2235")
            axes[0].hist(sizes, bins=30, color="#4f8ef7", alpha=0.85)
            axes[0].set_title("Keypoint scale distribution", color="#e2e8f0")
            axes[0].tick_params(colors="#64748b")
            axes[1].hist(responses, bins=30, color="#a855f7", alpha=0.85)
            axes[1].set_title("Response (strength) distribution", color="#e2e8f0")
            axes[1].tick_params(colors="#64748b")
            for ax in axes:
                for s in ax.spines.values(): s.set_color("#2a3a55")
            plt.tight_layout(); fig_to_st(fig)

    except cv2.error as e:
        st.warning(f"SIFT not available in this OpenCV build (requires opencv-contrib). Error: {e}")
        st.info("Showing ORB keypoints instead (always available).")
        orb = cv2.ORB_create(nfeatures=n_features)
        kps, _ = orb.detectAndCompute(gray, None)
        annotated = cv2.drawKeypoints(gray, kps, None, color=(0,200,100))
        st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)
        metric_row([("ORB Keypoints", len(kps))])

# ── TAB 2: HOG ─────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### HOG — Histogram of Oriented Gradients")
    theory_card(
        "HOG divides the image into cells (e.g. 8×8 pixels). For each cell, it computes "
        "a histogram of gradient orientations weighted by magnitude. "
        "Cells are grouped into overlapping blocks and normalised for illumination invariance. "
        "The concatenated histograms form a feature vector — widely used for pedestrian detection (DPM, early YOLO)."
    )
    cell_size  = st.select_slider("Cell size (pixels)", [4, 8, 16, 32], 8)
    nbins      = st.slider("Orientation bins", 6, 18, 9)
    block_size = st.select_slider("Block size (cells)", [1, 2, 3], 2)

    # Compute HOG manually for visualisation
    def compute_hog_viz(gray, cell=8, bins=9):
        """Return gradient magnitude/direction and HOG cell visualisation."""
        gx = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=1)
        gy = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1, ksize=1)
        mag, ang = cv2.cartToPolar(gx, gy, angleInDegrees=True)
        ang = ang % 180  # unsigned gradients

        h, w = gray.shape
        cell_h, cell_w = h//cell, w//cell
        hog_img = np.zeros((h, w), dtype=np.float32)

        for i in range(cell_h):
            for j in range(cell_w):
                mag_cell = mag[i*cell:(i+1)*cell, j*cell:(j+1)*cell]
                ang_cell = ang[i*cell:(i+1)*cell, j*cell:(j+1)*cell]
                hist, _ = np.histogram(ang_cell.flatten(), bins=bins, range=(0,180),
                                        weights=mag_cell.flatten())
                # Draw gradient lines in cell centre
                cy, cx = i*cell + cell//2, j*cell + cell//2
                for b in range(bins):
                    angle_rad = (b / bins) * np.pi
                    length    = min(cell//2 - 1, int(hist[b] / (hist.max()+1e-9) * (cell//2)))
                    x_end = int(cx + length * np.cos(angle_rad))
                    y_end = int(cy - length * np.sin(angle_rad))
                    x_st  = int(cx - length * np.cos(angle_rad))
                    y_st  = int(cy + length * np.sin(angle_rad))
                    cv2.line(hog_img, (x_st, y_st), (x_end, y_end), hist[b], 1)
        return mag, ang, hog_img

    resized = cv2.resize(gray, (256, 256))
    mag, ang, hog_viz = compute_hog_viz(resized, cell_size, nbins)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Gradient Magnitude**")
        st.image(((mag / mag.max()) * 255).astype(np.uint8), use_container_width=True, clamp=True)
    with c2:
        st.markdown("**Gradient Direction**")
        ang_norm = (ang / 180.0 * 255).astype(np.uint8)
        st.image(cv2.applyColorMap(ang_norm, cv2.COLORMAP_HSV),
                 use_container_width=True)
    with c3:
        st.markdown("**HOG Visualisation**")
        hog_display = ((hog_viz / (hog_viz.max()+1e-9)) * 255).astype(np.uint8)
        st.image(cv2.applyColorMap(hog_display, cv2.COLORMAP_INFERNO), use_container_width=True)

    # HOG feature vector stats
    h_img, w_img = resized.shape
    n_cells_y = h_img // cell_size
    n_cells_x = w_img // cell_size
    n_blocks_y = n_cells_y - block_size + 1
    n_blocks_x = n_cells_x - block_size + 1
    feat_dim   = n_blocks_y * n_blocks_x * block_size * block_size * nbins
    metric_row([
        ("Cells (Y×X)",      f"{n_cells_y}×{n_cells_x}"),
        ("Blocks (Y×X)",     f"{n_blocks_y}×{n_blocks_x}"),
        ("Feature dimension",f"{feat_dim:,}"),
        ("Bins per cell",     str(nbins)),
    ])

# ── TAB 3: ORB Matching ───────────────────────────────────────────────────────
with tab3:
    st.markdown("### ORB — Feature Matching")
    theory_card(
        "ORB (Oriented FAST and Rotated BRIEF) is a fast, patent-free alternative to SIFT. "
        "It uses FAST for keypoint detection and BRIEF for binary descriptors, enhanced with "
        "rotation invariance. Matching uses Hamming distance between binary descriptor strings. "
        "BFMatcher with cross-check finds consistent matches between two images."
    )
    st.markdown("Upload a second image to match against:")
    file2 = st.file_uploader("Second image for matching", type=["jpg","jpeg","png"], key="orb2")

    orb = cv2.ORB_create(nfeatures=500)
    kps1, des1 = orb.detectAndCompute(gray, None)

    if file2 is not None:
        from PIL import Image as PILImage
        img2 = np.array(PILImage.open(file2).convert("RGB"))
        gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
        kps2, des2 = orb.detectAndCompute(gray2, None)

        if des1 is not None and des2 is not None:
            bf      = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = sorted(bf.match(des1, des2), key=lambda x: x.distance)
            n_show  = st.slider("Show top N matches", 5, min(50, len(matches)), min(20, len(matches)))
            img_match = cv2.drawMatches(gray, kps1, gray2, kps2, matches[:n_show], None,
                                         flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            st.image(cv2.cvtColor(img_match, cv2.COLOR_BGR2RGB), use_container_width=True)
            metric_row([
                ("Keypoints img1",  len(kps1)),
                ("Keypoints img2",  len(kps2)),
                ("Total matches",   len(matches)),
                ("Showing",         n_show),
                ("Best distance",   f"{matches[0].distance:.0f}" if matches else "—"),
            ])
        else:
            st.warning("Could not compute ORB descriptors for one or both images.")
    else:
        st.info("Upload a second image above to see feature matching. In the meantime, here are the ORB keypoints on your first image:")
        annotated = cv2.drawKeypoints(gray, kps1, None, color=(0,200,100))
        st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)
        metric_row([("ORB Keypoints", len(kps1)), ("Descriptor size", "32 bytes (256 bits)")])

# ── TAB 4: Gradient Analysis ──────────────────────────────────────────────────
with tab4:
    st.markdown("### Gradient Analysis — Magnitude, Direction, and Edge Orientation")
    theory_card(
        "The image gradient at each pixel shows the direction of maximum intensity change. "
        "Magnitude = √(Gx²+Gy²) indicates edge strength. "
        "Direction = arctan(Gy/Gx) indicates edge orientation. "
        "The gradient direction is always perpendicular to the edge itself."
    )
    ksize = st.select_slider("Sobel kernel size", [1,3,5,7], 3)
    gx    = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=ksize)
    gy    = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=ksize)
    mag   = np.sqrt(gx**2 + gy**2)
    ang   = np.degrees(np.arctan2(gy, gx)) % 360

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), facecolor="#0b0f1a")
    for ax in axes.flat: ax.set_facecolor("#1a2235")

    axes[0,0].imshow(gray, cmap="gray"); axes[0,0].set_title("Original", color="#e2e8f0"); axes[0,0].axis("off")
    axes[0,1].imshow(np.abs(gx), cmap="RdBu_r"); axes[0,1].set_title("Sobel Gx (vertical edges)", color="#e2e8f0"); axes[0,1].axis("off")
    axes[0,2].imshow(np.abs(gy), cmap="RdBu_r"); axes[0,2].set_title("Sobel Gy (horizontal edges)", color="#e2e8f0"); axes[0,2].axis("off")
    axes[1,0].imshow(mag, cmap="hot"); axes[1,0].set_title("Gradient Magnitude", color="#e2e8f0"); axes[1,0].axis("off")
    axes[1,1].imshow(ang, cmap="hsv"); axes[1,1].set_title("Gradient Direction (colour = angle)", color="#e2e8f0"); axes[1,1].axis("off")

    # Orientation histogram
    axes[1,2].hist(ang.flatten(), bins=72, range=(0,360), color="#4f8ef7", alpha=0.85)
    axes[1,2].set_title("Orientation histogram", color="#e2e8f0")
    axes[1,2].set_xlabel("Angle (degrees)", color="#94a3b8")
    axes[1,2].tick_params(colors="#64748b")
    for s in axes[1,2].spines.values(): s.set_color("#2a3a55")

    plt.tight_layout(); fig_to_st(fig)
    metric_row([
        ("Max gradient magnitude", f"{mag.max():.1f}"),
        ("Mean magnitude",          f"{mag.mean():.1f}"),
        ("Dominant direction",       f"{ang.flatten()[np.argmax(np.histogram(ang.flatten(),72,(0,360))[0])]:.0f}°"),
    ])
