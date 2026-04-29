import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from utils.helpers import *



page_header(4, "Color, Wavelets & Morphology", "🎨",
    "Explore colour models, pseudo-colour mapping, wavelet decomposition, and morphological image processing.")

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
    img_rgb = upload_image("mod4")
    gray    = to_gray(img_rgb)

with tabs_container:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎨 Colour Models",
    "🌈 Pseudo-Color",
    "〰️ Wavelets",
    "◾ Morphological Ops",
    "🎯 Hit-or-Miss"
])

# ── TAB 1: Colour Models ───────────────────────────────────────────────────────
with tab1:
    st.markdown("### Colour Model Conversions")
    theory_box("Different colour spaces represent colour in different ways. RGB is device-oriented. "
               "HSV separates colour properties — useful for colour-based segmentation. "
               "LAB is perceptually uniform (equal distances = equal perceived differences). "
               "YCbCr separates luminance from chrominance — used in JPEG and TV standards.")

    model = st.selectbox("Colour space", ["RGB","HSV","LAB","YCbCr","CMY (pseudo)"])

    if model == "RGB":
        ch_names = ["Red","Green","Blue"]
        channels = [img_rgb[:,:,0], img_rgb[:,:,1], img_rgb[:,:,2]]
        cmaps    = ["Reds","Greens","Blues"]
    elif model == "HSV":
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        ch_names = ["Hue","Saturation","Value"]
        channels = [hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]]
        cmaps    = ["hsv","plasma","gray"]
    elif model == "LAB":
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        ch_names = ["L (Lightness)","A (green–red)","B (blue–yellow)"]
        channels = [lab[:,:,0], lab[:,:,1], lab[:,:,2]]
        cmaps    = ["gray","RdYlGn_r","bwr"]
    elif model == "YCbCr":
        ycbcr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
        ch_names = ["Y (Luma)","Cb (chroma blue)","Cr (chroma red)"]
        channels = [ycbcr[:,:,0], ycbcr[:,:,1], ycbcr[:,:,2]]
        cmaps    = ["gray","cool","hot"]
    else:
        r,g,b = img_rgb[:,:,0]/255., img_rgb[:,:,1]/255., img_rgb[:,:,2]/255.
        ch_names = ["Cyan (1-R)","Magenta (1-G)","Yellow (1-B)"]
        channels = [((1-r)*255).astype(np.uint8),((1-g)*255).astype(np.uint8),((1-b)*255).astype(np.uint8)]
        cmaps    = ["cyan","cool","YlOrBr"]

    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))
    axes[0].imshow(img_rgb); axes[0].set_title("Original RGB"); axes[0].axis("off")
    for i in range(3):
        axes[i+1].imshow(channels[i], cmap=cmaps[i])
        axes[i+1].set_title(ch_names[i]); axes[i+1].axis("off")
    plt.tight_layout(); fig_to_st(fig)

    theory_box(f"Current space: {model}. " + {
        "RGB": "Additive primaries. Equal R=G=B gives grey.",
        "HSV": "H ∈ [0,179°], S ∈ [0,255], V ∈ [0,255]. Good for skin/object detection.",
        "LAB": "L* = 0 (black) to 100 (white). A* and B* are chrominance axes.",
        "YCbCr": "JPEG and video use this. Y = 0.299R+0.587G+0.114B.",
        "CMY (pseudo)": "Subtractive model used in printing. Ink absorbs colour."
    }.get(model,""))

# ── TAB 2: Pseudo-Color ────────────────────────────────────────────────────────
with tab2:
    st.markdown("### Pseudo-Color Image Processing")
    theory_box("Pseudo-colour maps grayscale intensity values to colours using a colour look-up table (LUT). "
               "It does NOT add real colour information — it enhances visual discrimination between "
               "intensity regions that look similar in greyscale. Widely used in medical imaging, "
               "thermal cameras, and satellite imagery.")

    colormaps = {
        "Jet (thermal-style)": cv2.COLORMAP_JET,
        "Hot":                 cv2.COLORMAP_HOT,
        "Rainbow":             cv2.COLORMAP_RAINBOW,
        "Ocean":               cv2.COLORMAP_OCEAN,
        "HSV":                 cv2.COLORMAP_HSV,
        "Inferno":             cv2.COLORMAP_INFERNO,
        "Turbo":               cv2.COLORMAP_TURBO,
        "Viridis":             cv2.COLORMAP_VIRIDIS,
    }
    cmap_name = st.selectbox("Colour map", list(colormaps.keys()))
    pseudo = cv2.applyColorMap(gray, colormaps[cmap_name])
    pseudo_rgb = cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB)

    show_images([(gray,"Grayscale input"),(pseudo_rgb,f"Pseudo-color: {cmap_name}")], n_cols=2)

    st.markdown("#### Intensity band isolation")
    theory_box("Slicing isolates a specific intensity range and maps it to a colour. Pixels outside "
               "the range are shown in grey. This highlights structures within a specific density range.")
    lo = st.slider("Lower intensity bound", 0, 254, 80)
    hi = st.slider("Upper intensity bound", lo+1, 255, 180)
    mask = (gray >= lo) & (gray <= hi)
    sliced = np.stack([gray]*3, axis=-1).copy()
    sliced[mask] = [255, 100, 0]
    sliced[~mask] = np.stack([gray[~mask]]*3, axis=-1)
    st.image(sliced, caption=f"Intensity band [{lo}–{hi}] highlighted in orange", use_container_width=True)

# ── TAB 3: Wavelets ────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### Wavelet Decomposition")
    theory_box("Wavelets provide multi-resolution analysis — they decompose an image into approximation "
               "(low-frequency) and detail (high-frequency) sub-bands simultaneously. "
               "Each decomposition level halves the resolution. The approximation captures the overall "
               "structure; horizontal/vertical/diagonal details capture edges in those orientations. "
               "Used in JPEG-2000 compression.")

    try:
        import pywt
        wavelet = st.selectbox("Wavelet family", ["haar","db2","db4","sym4","coif1","bior2.2"])
        level   = st.slider("Decomposition level", 1, 4, 2)

        coeffs = pywt.wavedec2(gray.astype(float), wavelet, level=level)
        cA = coeffs[0]
        titles = [f"Approximation (level {level})"]
        imgs_w = [normalize_display(cA)]

        for lvl_idx, (cH, cV, cD) in enumerate(coeffs[1:], 1):
            lbl = level - lvl_idx + 1
            imgs_w += [normalize_display(cH), normalize_display(cV), normalize_display(cD)]
            titles += [f"Horizontal detail (L{lbl})", f"Vertical detail (L{lbl})", f"Diagonal detail (L{lbl})"]

        n = len(imgs_w)
        ncols = 4
        nrows = (n + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.5*nrows))
        axes = np.array(axes).flatten()
        for i, (im, tt) in enumerate(zip(imgs_w, titles)):
            axes[i].imshow(im, cmap="gray"); axes[i].set_title(tt, fontsize=9); axes[i].axis("off")
        for i in range(len(imgs_w), len(axes)):
            axes[i].axis("off")
        plt.tight_layout(); fig_to_st(fig)

        # Reconstruction
        if st.checkbox("Show wavelet compression (zero out detail coefficients)"):
            keep_pct = st.slider("Keep largest % of coefficients", 1, 100, 10)
            all_coeffs = np.concatenate([c.flatten() for arr in coeffs[1:] for c in arr])
            thresh = np.percentile(np.abs(all_coeffs), 100-keep_pct)
            coeffs_thresh = [coeffs[0]] + [
                tuple(np.where(np.abs(c) > thresh, c, 0) for c in level_coeffs)
                for level_coeffs in coeffs[1:]
            ]
            reconstructed = pywt.waverec2(coeffs_thresh, wavelet)
            r_uint8 = normalize_display(reconstructed[:gray.shape[0], :gray.shape[1]])
            show_images([(gray,"Original"),(r_uint8,f"Reconstructed ({keep_pct}% coefficients kept)")], n_cols=2)
            metric_row([("PSNR",f"{psnr(gray.astype(np.uint8),r_uint8):.1f} dB"),
                        ("Coefficients kept",f"{keep_pct}%"),
                        ("Compression ratio",f"{100/keep_pct:.1f}×")])

    except ImportError:
        st.warning("PyWavelets not installed. Run: `pip install PyWavelets`")
        st.info("Showing simulated multi-resolution pyramid instead.")
        for i in range(3):
            small = cv2.resize(gray, (gray.shape[1]//(2**i), gray.shape[0]//(2**i)))
            st.image(small, caption=f"Level {i} approximation ({small.shape[1]}×{small.shape[0]})", use_container_width=True)

# ── TAB 4: Morphological Operations ───────────────────────────────────────────
with tab4:
    st.markdown("### Morphological Image Processing")
    theory_box("Morphological operations process images based on shapes using a structuring element (SE). "
               "Erosion shrinks bright regions, removes small objects. Dilation expands bright regions, fills gaps. "
               "Opening (erosion then dilation) removes small bright noise. "
               "Closing (dilation then erosion) fills small dark holes. "
               "Gradient = Dilation − Erosion = boundary extraction.")

    # Binarise first
    thresh_val = st.slider("Binary threshold (pre-processing)", 0, 255, 127)
    _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)

    op = st.selectbox("Operation", [
        "Erosion","Dilation","Opening","Closing",
        "Morphological Gradient","Top-Hat","Black-Hat","Skeletonisation"])

    se_shape = st.radio("Structuring element shape", ["Rectangle","Ellipse","Cross"], horizontal=True)
    se_size  = st.slider("SE size", 3, 31, 5, step=2)

    shape_map = {"Rectangle": cv2.MORPH_RECT, "Ellipse": cv2.MORPH_ELLIPSE, "Cross": cv2.MORPH_CROSS}
    kernel = cv2.getStructuringElement(shape_map[se_shape], (se_size, se_size))

    morph_map = {
        "Erosion":               (cv2.MORPH_ERODE,    "Shrinks bright regions. Removes protrusions smaller than SE."),
        "Dilation":              (cv2.MORPH_DILATE,   "Expands bright regions. Fills small gaps within bright areas."),
        "Opening":               (cv2.MORPH_OPEN,     "Erosion → Dilation. Removes small bright objects (noise)."),
        "Closing":               (cv2.MORPH_CLOSE,    "Dilation → Erosion. Fills small dark holes inside bright regions."),
        "Morphological Gradient":(cv2.MORPH_GRADIENT, "Dilation − Erosion. Extracts boundary of objects."),
        "Top-Hat":               (cv2.MORPH_TOPHAT,   "Input − Opening. Extracts small bright details on dark background."),
        "Black-Hat":             (cv2.MORPH_BLACKHAT, "Closing − Input. Extracts small dark details on bright background."),
    }

    if op == "Skeletonisation":
        img_sk = binary.copy()
        skel = np.zeros_like(img_sk)
        kernel_sk = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
        iterations = 0
        while True:
            eroded   = cv2.erode(img_sk, kernel_sk)
            temp     = cv2.dilate(eroded, kernel_sk)
            temp     = cv2.subtract(img_sk, temp)
            skel     = cv2.bitwise_or(skel, temp)
            img_sk   = eroded.copy()
            iterations += 1
            if cv2.countNonZero(img_sk) == 0 or iterations > 100:
                break
        show_images([(binary,"Binary input"),(skel,f"Skeleton ({iterations} iterations)")], n_cols=2)
        theory_box("Skeletonisation reduces binary objects to a 1-pixel-wide medial axis using repeated erosion + subtraction.")
    else:
        mtype, explanation = morph_map[op]
        if op in ("Erosion","Dilation"):
            iters = st.slider("Iterations", 1, 10, 1)
            result = cv2.morphologyEx(binary, mtype, kernel, iterations=iters)
        else:
            result = cv2.morphologyEx(binary, mtype, kernel)
        show_images([(binary,"Binary input"),(result,f"{op} output")], n_cols=2)
        theory_box(explanation)

    # Show structuring element
    if st.checkbox("Visualise structuring element"):
        se_disp = cv2.resize(kernel * 255, (100, 100), interpolation=cv2.INTER_NEAREST)
        st.image(se_disp, caption=f"{se_shape} SE ({se_size}×{se_size})", width=150)

# ── TAB 5: Hit-or-Miss ────────────────────────────────────────────────────────
with tab5:
    st.markdown("### Hit-or-Miss Transform")
    theory_box("The Hit-or-Miss transform detects specific binary patterns. It uses two complementary SEs: "
               "B1 (foreground pattern to match) and B2 (background pattern around it). "
               "A pixel is marked only if B1 fits within the object AND B2 fits outside it simultaneously. "
               "Used for detecting isolated points, line ends, corners, and specific shapes.")

    pattern = st.selectbox("Pattern to detect", [
        "Isolated foreground pixel",
        "Top-right corner",
        "Horizontal line end (right)",
        "Custom 3×3 pattern"
    ])

    thresh2 = st.slider("Binary threshold", 0, 255, 127, key="hmt")
    _, bin2 = cv2.threshold(gray, thresh2, 255, cv2.THRESH_BINARY)

    if pattern == "Isolated foreground pixel":
        b1 = np.array([[0,0,0],[0,1,0],[0,0,0]], dtype=np.int8)
        b2 = np.array([[1,1,1],[1,0,1],[1,1,1]], dtype=np.int8)
        desc = "Detects pixels that are ON with all 8 neighbours OFF (isolated dots)."
    elif pattern == "Top-right corner":
        b1 = np.array([[0,1,1],[0,1,1],[0,0,0]], dtype=np.int8)
        b2 = np.array([[1,0,0],[1,0,0],[1,1,1]], dtype=np.int8)
        desc = "Detects top-right corners in binary shapes."
    elif pattern == "Horizontal line end (right)":
        b1 = np.array([[0,0,0],[1,1,0],[0,0,0]], dtype=np.int8)
        b2 = np.array([[1,1,1],[0,0,1],[1,1,1]], dtype=np.int8)
        desc = "Detects right endpoints of horizontal lines."
    else:
        st.markdown("**Define 3×3 pattern (1=foreground, 0=background, -1=don't care):**")
        cols_hm = st.columns(3)
        b1_flat = []; b2_flat = []
        for i in range(9):
            val = cols_hm[i%3].selectbox(f"({i//3},{i%3})", [1,0,-1], index=2, key=f"hm{i}")
            b1_flat.append(1 if val==1 else 0)
            b2_flat.append(1 if val==0 else 0)
        b1 = np.array(b1_flat, dtype=np.int8).reshape(3,3)
        b2 = np.array(b2_flat, dtype=np.int8).reshape(3,3)
        desc = "Custom pattern defined above."

    bin_norm = (bin2 // 255).astype(np.uint8)
    erode1 = cv2.erode(bin_norm, b1.clip(0,1))
    erode2 = cv2.erode(1 - bin_norm, b2.clip(0,1))
    result_hm = cv2.bitwise_and(erode1, erode2) * 255

    show_images([(bin2,"Binary input"),(result_hm,"Hit-or-Miss result")], n_cols=2)
    theory_box(desc + f" Detected pixels: {(result_hm > 0).sum()}")
