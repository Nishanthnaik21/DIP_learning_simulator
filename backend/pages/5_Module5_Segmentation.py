import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from utils.helpers import *



page_header(5, "Image Segmentation", "✂️",
    "Detect discontinuities, apply edge detection, Hough transforms, thresholding, corner detection, and extract boundary descriptors.")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


# ── Containers for layout ordering ─────────────────────────────────────────────
tabs_container = st.container()
st.markdown("<br><br>", unsafe_allow_html=True)
upload_container = st.container()

with upload_container:
    st.markdown("### 🖼️ Change Image")
    img_rgb = upload_image("mod5")
    gray    = to_gray(img_rgb)

with tabs_container:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔪 Edge Detection",
    "📐 Hough Transforms",
    "🔲 Thresholding",
    "◆ Corner Detection",
    "📏 Boundary Descriptors"
])

# ── TAB 1: Edge Detection ──────────────────────────────────────────────────────
with tab1:
    st.markdown("### Edge Detection")
    theory_box("Edges are boundaries between regions of different intensity. "
               "First-derivative operators (Sobel, Prewitt, Roberts): detect edges as local maxima of gradient. "
               "Laplacian of Gaussian (LoG): second derivative, detects zero-crossings. "
               "Canny: multi-stage — Gaussian smooth → gradient → non-maximum suppression → double thresholding → hysteresis.")

    detector = st.selectbox("Edge detector", [
        "Sobel (X)","Sobel (Y)","Sobel (combined)","Prewitt","Roberts Cross",
        "Laplacian","LoG (Marr-Hildreth)","Canny"])

    blurred = cv2.GaussianBlur(gray, (5,5), 1.4)

    if detector == "Sobel (X)":
        out = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
        theory_box("Sobel X detects vertical edges (intensity changes in X direction). Kernel: [[-1,0,1],[-2,0,2],[-1,0,1]]")
    elif detector == "Sobel (Y)":
        out = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
        theory_box("Sobel Y detects horizontal edges (intensity changes in Y direction). Kernel: [[-1,-2,-1],[0,0,0],[1,2,1]]")
    elif detector == "Sobel (combined)":
        sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        out = cv2.convertScaleAbs(np.sqrt(sx**2 + sy**2))
        theory_box("Combined Sobel: magnitude = √(Gx² + Gy²). Direction = arctan(Gy/Gx).")
    elif detector == "Prewitt":
        kx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)
        ky = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=np.float32)
        px = cv2.filter2D(gray.astype(np.float32), -1, kx)
        py = cv2.filter2D(gray.astype(np.float32), -1, ky)
        out = cv2.convertScaleAbs(np.sqrt(px**2 + py**2))
        theory_box("Prewitt operator: similar to Sobel but without the centre-weight emphasis. Equal weights in all rows.")
    elif detector == "Roberts Cross":
        kr1 = np.array([[1,0],[0,-1]], dtype=np.float32)
        kr2 = np.array([[0,1],[-1,0]], dtype=np.float32)
        r1  = cv2.filter2D(gray.astype(np.float32), -1, kr1)
        r2  = cv2.filter2D(gray.astype(np.float32), -1, kr2)
        out = cv2.convertScaleAbs(np.sqrt(r1**2 + r2**2))
        theory_box("Roberts Cross: 2×2 diagonal difference operator. Fast, sensitive to noise, best for sharp clean edges.")
    elif detector == "Laplacian":
        ksize = st.slider("Kernel size", 1, 7, 3, step=2)
        out = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_32F, ksize=ksize))
        theory_box(f"Laplacian ∇²f detects all edges (isotropic). Second derivative — sensitive to noise. Kernel {ksize}×{ksize}.")
    elif detector == "LoG (Marr-Hildreth)":
        sigma = st.slider("Gaussian sigma", 0.5, 5.0, 1.5)
        size  = st.slider("Kernel size", 3, 21, 9, step=2)
        smoothed = cv2.GaussianBlur(gray, (size,size), sigma)
        log = cv2.Laplacian(smoothed, cv2.CV_32F)
        out = cv2.convertScaleAbs(log)
        theory_box(f"LoG = Laplacian(Gaussian(σ={sigma})). First smooth to reduce noise, then find zero-crossings of second derivative.")
    else:  # Canny
        t1 = st.slider("Low threshold", 10, 200, 50)
        t2 = st.slider("High threshold", t1, 400, 150)
        aperture = st.select_slider("Aperture", [3,5,7], 3)
        out = cv2.Canny(gray, t1, t2, apertureSize=aperture)
        theory_box(f"Canny: Gaussian smooth → Sobel gradient → NMS → double threshold [{t1},{t2}] → hysteresis. "
                   "Best all-round edge detector. Strong edges > {t2}; weak edges {t1}–{t2} kept only if connected to strong.")

    show_images([(gray,"Original"),(out,"Edge map")], n_cols=2)
    metric_row([("Edge pixels",f"{(out>0).sum():,}"),
                ("Edge density",f"{(out>0).mean()*100:.1f}%"),
                ("Image size",f"{gray.shape[1]}×{gray.shape[0]}")])

# ── TAB 2: Hough Transforms ────────────────────────────────────────────────────
with tab2:
    st.markdown("### Hough Transforms")
    theory_box("Hough transform maps points in image space to parameter space (Hough space). "
               "For lines: each edge pixel votes for all possible (ρ, θ) lines through it. "
               "Peaks in Hough space = lines in image space. "
               "Circular Hough: each edge pixel votes for all circles with given radius. "
               "Shape Detection: generalised Hough for arbitrary shapes.")

    htype = st.radio("Transform type", ["Line detection","Probabilistic line detection","Circle detection"], horizontal=True)
    edges = cv2.Canny(gray, 50, 150)
    result = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    if htype == "Line detection":
        threshold = st.slider("Accumulator threshold", 30, 200, 80)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold)
        count = 0
        if lines is not None:
            for line in lines[:50]:
                rho, theta = line[0]
                a, b = np.cos(theta), np.sin(theta)
                x0, y0 = a*rho, b*rho
                x1 = int(x0 + 1000*(-b)); y1 = int(y0 + 1000*a)
                x2 = int(x0 - 1000*(-b)); y2 = int(y0 - 1000*a)
                cv2.line(result, (x1,y1), (x2,y2), (255,100,0), 1)
                count += 1
        show_images([(edges,"Edge map"),(result,f"Hough lines ({count} detected)")], n_cols=2)
        theory_box(f"Standard Hough: each edge pixel votes in (ρ,θ) space. Lines where votes > {threshold} are detected. Found {count} lines.")

    elif htype == "Probabilistic line detection":
        min_len = st.slider("Min line length", 10, 200, 50)
        max_gap = st.slider("Max line gap", 1, 100, 10)
        threshold_p = st.slider("Threshold", 20, 150, 50)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold_p, minLineLength=min_len, maxLineGap=max_gap)
        count = 0
        if lines is not None:
            for line in lines:
                x1,y1,x2,y2 = line[0]
                cv2.line(result, (x1,y1), (x2,y2), (255,100,0), 2)
                count += 1
        show_images([(edges,"Edge map"),(result,f"PHT lines ({count} detected)")], n_cols=2)
        theory_box(f"Probabilistic HT: finds actual line segments (with endpoints) rather than infinite lines. Min length={min_len}, Max gap={max_gap}.")

    else:
        dp = st.slider("Inverse ratio dp", 1.0, 3.0, 1.5)
        min_dist = st.slider("Min distance between centres", 10, 100, 30)
        p1 = st.slider("Canny high threshold", 30, 200, 80)
        p2 = st.slider("Accumulator threshold", 10, 100, 30)
        min_r = st.slider("Min radius", 5, 50, 10)
        max_r = st.slider("Max radius", 20, min(gray.shape)//2, 60)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, min_dist, param1=p1, param2=p2, minRadius=min_r, maxRadius=max_r)
        count = 0
        if circles is not None:
            circles = np.round(circles[0,:]).astype(int)
            for (x,y,r) in circles:
                cv2.circle(result, (x,y), r, (0,200,255), 2)
                cv2.circle(result, (x,y), 2, (255,100,0), 3)
                count += 1
        show_images([(gray,"Original"),(result,f"Hough circles ({count} detected)")], n_cols=2)
        theory_box(f"Circle Hough: votes in (x_c, y_c, r) space. Detected {count} circles.")

# ── TAB 3: Thresholding ────────────────────────────────────────────────────────
with tab3:
    st.markdown("### Thresholding Methods")
    theory_box("Thresholding converts a grayscale image to binary by classifying pixels as foreground or background. "
               "Global Otsu automatically finds the optimal threshold by minimising intra-class variance. "
               "Adaptive thresholding computes a local threshold for each pixel neighbourhood — better for uneven lighting. "
               "Multi-level thresholding creates multiple classes.")

    method = st.selectbox("Thresholding method", [
        "Manual global","Otsu's method","Triangle method",
        "Adaptive (mean)","Adaptive (Gaussian)","Multi-level Otsu"])

    blurred_t = cv2.GaussianBlur(gray, (5,5), 0)

    if method == "Manual global":
        T = st.slider("Threshold T", 0, 255, 127)
        _, out = cv2.threshold(gray, T, 255, cv2.THRESH_BINARY)
        theory_box(f"Binary: pixel = 255 if I > {T} else 0.")
    elif method == "Otsu's method":
        T, out = cv2.threshold(blurred_t, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        theory_box(f"Otsu found optimal threshold T={T:.0f} by maximising between-class variance. No manual tuning needed.")
    elif method == "Triangle method":
        T, out = cv2.threshold(blurred_t, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
        theory_box(f"Triangle method: finds threshold at the point furthest from the line connecting histogram peak to its end. T={T:.0f}")
    elif method == "Adaptive (mean)":
        block = st.slider("Block size (must be odd)", 3, 99, 11, step=2)
        C     = st.slider("Constant C", -30, 30, 2)
        out   = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block, C)
        theory_box(f"Each pixel's threshold = mean of {block}×{block} neighbourhood minus C={C}. Good for uneven illumination.")
    elif method == "Adaptive (Gaussian)":
        block = st.slider("Block size", 3, 99, 11, step=2)
        C     = st.slider("Constant C", -30, 30, 2)
        out   = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, C)
        theory_box(f"Each pixel's threshold = Gaussian-weighted sum of {block}×{block} neighbourhood minus {C}. Smoother transitions than mean.")
    else:
        num_classes = st.slider("Number of classes", 2, 5, 3)
        hist = cv2.calcHist([gray],[0],None,[256],[0,256]).flatten()
        def multi_otsu(hist, n):
            thresholds = [0]
            remaining = gray.copy()
            for _ in range(n-1):
                _, t = cv2.threshold(remaining, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                thresholds.append(int(t))
                remaining = np.where(remaining > t, remaining, 0).astype(np.uint8)
            return sorted(set(thresholds[1:]))
        ts = multi_otsu(hist, num_classes)
        out = np.zeros_like(gray)
        boundaries = [0] + ts + [255]
        for i in range(len(boundaries)-1):
            mask = (gray >= boundaries[i]) & (gray < boundaries[i+1])
            out[mask] = int(255 * i / (len(boundaries)-2))
        theory_box(f"Multi-level: threshold values = {ts}. Creates {num_classes} intensity classes.")

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    axes[0].imshow(gray, cmap="gray"); axes[0].set_title("Original"); axes[0].axis("off")
    axes[1].imshow(out, cmap="gray");  axes[1].set_title(f"{method}"); axes[1].axis("off")
    hist2 = cv2.calcHist([gray],[0],None,[256],[0,256]).flatten()
    axes[2].bar(range(256), hist2, color="#4f6ef7", width=1)
    axes[2].set_title("Histogram"); axes[2].set_xlabel("Intensity")
    plt.tight_layout(); fig_to_st(fig)
    metric_row([("Foreground %",f"{(out>0).mean()*100:.1f}%"),
                ("Background %",f"{(out==0).mean()*100:.1f}%")])

# ── TAB 4: Corner Detection ────────────────────────────────────────────────────
with tab4:
    st.markdown("### Corner Detection")
    theory_box("Corners are points where intensity changes significantly in multiple directions. "
               "Harris detector computes second-moment matrix M of gradients. Corner response R = det(M) − k·trace(M)². "
               "Shi-Tomasi (Good Features to Track): uses min eigenvalue of M — more stable. "
               "FAST: tests pixels on a circle around each point — very fast for real-time applications.")

    detector_c = st.selectbox("Corner detector", ["Harris","Shi-Tomasi (Good Features)","FAST"])
    overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    if detector_c == "Harris":
        block  = st.slider("Block size", 2, 10, 2)
        ksize  = st.select_slider("Sobel kernel size", [3,5,7], 3)
        k      = st.slider("Harris k parameter", 0.01, 0.1, 0.04)
        thresh = st.slider("Response threshold %", 1, 50, 10)
        dst    = cv2.cornerHarris(gray, block, ksize, k)
        dst    = cv2.dilate(dst, None)
        T_val  = thresh/100.0 * dst.max()
        overlay[dst > T_val] = [255, 0, 0]
        count  = (dst > T_val).sum()
        show_images([(gray,"Original"),(overlay,f"Harris corners ({count} detected)")], n_cols=2)
        theory_box(f"R = det(M) − {k}·trace(M)². High R = corner. Negative R = edge. R≈0 = flat. Found {count} corners.")

    elif detector_c == "Shi-Tomasi (Good Features)":
        max_corners = st.slider("Max corners to detect", 10, 500, 100)
        quality     = st.slider("Quality level", 0.001, 0.1, 0.01, format="%.3f")
        min_dist    = st.slider("Min distance", 5, 50, 10)
        corners     = cv2.goodFeaturesToTrack(gray, max_corners, quality, min_dist)
        if corners is not None:
            corners = np.int0(corners)
            for c in corners:
                x,y = c.ravel()
                cv2.circle(overlay, (x,y), 4, (255,100,0), -1)
        count = len(corners) if corners is not None else 0
        show_images([(gray,"Original"),(overlay,f"Shi-Tomasi ({count} corners)")], n_cols=2)
        theory_box(f"Shi-Tomasi: min eigenvalue of M > quality×max_eigenvalue. More stable than Harris. Found {count} corners.")

    else:
        threshold_f = st.slider("FAST threshold", 1, 100, 10)
        use_nms     = st.checkbox("Non-maximum suppression", value=True)
        fast        = cv2.FastFeatureDetector_create(threshold=threshold_f, nonmaxSuppression=use_nms)
        kps         = fast.detect(gray)
        for kp in kps:
            x, y = int(kp.pt[0]), int(kp.pt[1])
            cv2.circle(overlay, (x,y), 3, (0,255,100), -1)
        show_images([(gray,"Original"),(overlay,f"FAST corners ({len(kps)} keypoints)")], n_cols=2)
        theory_box(f"FAST tests 16 pixels on a circle (r=3) around each candidate. Threshold={threshold_f}. Detected {len(kps)} keypoints.")

# ── TAB 5: Boundary Descriptors ────────────────────────────────────────────────
with tab5:
    st.markdown("### Boundary Descriptors & Representation")
    theory_box("After segmentation, regions are described using boundary and region descriptors. "
               "Boundary descriptors: perimeter, chain code, Fourier descriptors. "
               "Region descriptors: area, centroid, Hu moments (invariant to rotation/scale/translation), "
               "eccentricity, and bounding box. These features are used for shape classification and recognition.")

    thresh_bd = st.slider("Binary threshold", 0, 255, 127, key="bd")
    _, binary_bd = cv2.threshold(gray, thresh_bd, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary_bd, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    overlay_bd = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(overlay_bd, contours, -1, (255,100,0), 2)
    show_images([(binary_bd,"Binary image"),(overlay_bd,f"Contours ({len(contours)} found)")], n_cols=2)

    if contours:
        # Sort by area, pick top N
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
        num_show = st.slider("Show descriptors for top N contours", 1, min(10,len(contours_sorted)), min(5,len(contours_sorted)))
        st.markdown(f"### Descriptors for {num_show} largest regions")

        for i, cnt in enumerate(contours_sorted[:num_show]):
            area      = cv2.contourArea(cnt)
            perim     = cv2.arcLength(cnt, True)
            M_cnt     = cv2.moments(cnt)
            circularity = (4*np.pi*area / (perim**2)) if perim > 0 else 0
            if M_cnt["m00"] > 0:
                cx = M_cnt["m10"]/M_cnt["m00"]
                cy = M_cnt["m01"]/M_cnt["m00"]
            else:
                cx, cy = 0, 0

            # Hu moments
            hu = cv2.HuMoments(M_cnt).flatten()

            # Bounding box
            x,y,w,h = cv2.boundingRect(cnt)
            aspect   = w/h if h>0 else 0
            ecc      = w/h if h>0 else 1  # simplified

            with st.expander(f"Contour {i+1} | Area={area:.0f} px²"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Area (px²)", f"{area:.0f}")
                c2.metric("Perimeter (px)", f"{perim:.1f}")
                c3.metric("Circularity", f"{circularity:.3f}")
                c1.metric("Centroid X", f"{cx:.1f}")
                c2.metric("Centroid Y", f"{cy:.1f}")
                c3.metric("Aspect ratio (W/H)", f"{aspect:.2f}")

                st.markdown("**Hu Moments** (rotation/scale/translation invariant):")
                hu_labels = [f"h{i+1}" for i in range(7)]
                hu_vals   = [f"{h:.4e}" for h in hu]
                hu_df     = dict(zip(hu_labels, hu_vals))
                st.json(hu_df)

                theory_box("Circularity = 4πA/P². Circle=1.0, square≈0.785, elongated≈0. "
                           "Hu moments h1–h7 are invariant to geometric transformations — used as shape fingerprints.")
