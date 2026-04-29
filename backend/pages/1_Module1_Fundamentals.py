import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from utils.helpers import *



page_header(1, "Digital Image Fundamentals", "🖼️",
    "Explore pixel values, image sampling, quantization, colour channels, and basic image operations.")

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
    img_rgb = upload_image("mod1")
    gray    = to_gray(img_rgb)

with tabs_container:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Pixel Inspector",
    "📉 Sampling & Quantization",
    "🎨 Colour Channels",
    "➕ Linear Operations",
    "📊 Image Statistics"
])

# ── TAB 1: Pixel Inspector ─────────────────────────────────────────────────────
with tab1:
    st.markdown("### Pixel Neighbourhood Inspector")
    theory_box("A digital image is a 2D matrix of pixel intensity values. Each pixel has a spatial position (x,y) "
               "and an intensity value. 4-connectivity uses up/down/left/right neighbours. "
               "8-connectivity adds the 4 diagonal neighbours.")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(img_rgb, caption="Input image", use_container_width=True)
    with c2:
        h, w = gray.shape
        px = st.slider("Pixel X (column)", 1, w-2, w//2)
        py = st.slider("Pixel Y (row)", 1, h-2, h//2)

        val = gray[py, px]
        st.markdown(f"**Selected pixel ({px}, {py}):** intensity = `{val}`")

        # 3×3 neighbourhood
        patch = gray[py-1:py+2, px-1:px+2]
        st.markdown("**3×3 neighbourhood matrix:**")
        st.dataframe(patch, hide_index=False)

        # 4 and 8 neighbours
        n4 = {
            "Up":    int(gray[py-1, px]),
            "Down":  int(gray[py+1, px]),
            "Left":  int(gray[py, px-1]),
            "Right": int(gray[py, px+1]),
        }
        n8_extra = {
            "UL": int(gray[py-1,px-1]), "UR": int(gray[py-1,px+1]),
            "DL": int(gray[py+1,px-1]), "DR": int(gray[py+1,px+1]),
        }
        st.markdown("**4-neighbours:** " + "  |  ".join([f"{k}={v}" for k,v in n4.items()]))
        st.markdown("**8-neighbours (diagonals):** " + "  |  ".join([f"{k}={v}" for k,v in n8_extra.items()]))

        if len(img_rgb.shape) == 3:
            r,g,b = img_rgb[py,px]
            metric_row([("R channel",int(r)),("G channel",int(g)),("B channel",int(b))])

# ── TAB 2: Sampling & Quantization ────────────────────────────────────────────
with tab2:
    st.markdown("### Image Sampling & Quantization")
    theory_box("Sampling controls spatial resolution — reducing it removes detail and creates the 'pixelated' effect. "
               "Quantization controls how many grey levels are used. At 1-bit, only black/white remains. "
               "Both demonstrate the fundamental digital image formation process.")

    c1, c2 = st.columns(2)
    with c1:
        factor = st.slider("Sampling factor (downsample × then upsample)", 1, 16, 1)
        small = cv2.resize(gray, (max(1,gray.shape[1]//factor), max(1,gray.shape[0]//factor)),
                           interpolation=cv2.INTER_NEAREST)
        restored = cv2.resize(small, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_NEAREST)
        st.image(restored, caption=f"Sampling factor ×{factor} ({small.shape[1]}×{small.shape[0]} px)",
                 use_container_width=True, clamp=True)

    with c2:
        bits = st.slider("Quantization bits (grey levels)", 1, 8, 8)
        levels = 2**bits
        q_img = (gray // (256 // levels)) * (256 // levels)
        st.image(q_img, caption=f"{bits}-bit quantization ({levels} grey levels)",
                 use_container_width=True, clamp=True)

    theory_box(f"Current: {gray.shape[1]}×{gray.shape[0]} pixels, {bits}-bit = {levels} grey levels. "
               "Original 8-bit = 256 levels. Reducing bits shows banding/contouring artefacts.")

# ── TAB 3: Colour Channels ────────────────────────────────────────────────────
with tab3:
    st.markdown("### Colour Channel Separation")
    theory_box("An RGB image has 3 channels — Red, Green, Blue. Each pixel's colour is a combination of these. "
               "Separating channels helps understand colour composition. HSV separates Hue (colour), "
               "Saturation (vividness), and Value (brightness) — useful for colour-based segmentation.")

    mode = st.radio("Colour space", ["RGB Channels", "HSV Channels", "YCbCr Channels"], horizontal=True)

    if mode == "RGB Channels":
        r = img_rgb[:,:,0]; g = img_rgb[:,:,1]; b = img_rgb[:,:,2]
        show_images([(img_rgb,"Original RGB"),(r,"Red channel"),(g,"Green channel"),(b,"Blue channel")], n_cols=4)
    elif mode == "HSV Channels":
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        show_images([(img_rgb,"Original RGB"),
                     (hsv[:,:,0],"Hue"),(hsv[:,:,1],"Saturation"),(hsv[:,:,2],"Value")], n_cols=4)
    else:
        ycbcr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
        show_images([(img_rgb,"Original RGB"),
                     (ycbcr[:,:,0],"Y (Luma)"),(ycbcr[:,:,1],"Cb"),(ycbcr[:,:,2],"Cr")], n_cols=4)

# ── TAB 4: Linear / Nonlinear Operations ──────────────────────────────────────
with tab4:
    st.markdown("### Linear & Nonlinear Operations")
    theory_box("Linear operations satisfy superposition: output = a×input + b. "
               "Examples: brightness/contrast adjustment. Nonlinear operations include gamma correction, "
               "log transform, and thresholding — they change the shape of the intensity mapping curve.")

    op = st.selectbox("Operation", [
        "Brightness adjustment (linear)",
        "Contrast adjustment (linear)",
        "Gamma correction (nonlinear)",
        "Log transform (nonlinear)",
        "Negative image",
        "Thresholding (nonlinear)"
    ])

    c1, c2 = st.columns(2)
    with c1:
        st.image(gray, caption="Original (grayscale)", use_container_width=True, clamp=True)

    with c2:
        if op == "Brightness adjustment (linear)":
            b = st.slider("Brightness offset (b)", -100, 100, 30)
            out = np.clip(gray.astype(int) + b, 0, 255).astype(np.uint8)
            st.image(out, caption=f"I_out = I_in + {b}", use_container_width=True, clamp=True)

        elif op == "Contrast adjustment (linear)":
            a = st.slider("Contrast scale (a)", 0.1, 3.0, 1.5)
            out = np.clip(gray.astype(float) * a, 0, 255).astype(np.uint8)
            st.image(out, caption=f"I_out = {a:.1f} × I_in", use_container_width=True, clamp=True)

        elif op == "Gamma correction (nonlinear)":
            gamma = st.slider("Gamma (γ)", 0.1, 4.0, 1.0)
            lut = np.array([((i/255.0)**gamma)*255 for i in range(256)], dtype=np.uint8)
            out = cv2.LUT(gray, lut)
            st.image(out, caption=f"I_out = I_in^{gamma:.2f}", use_container_width=True, clamp=True)
            theory_box(f"γ < 1 brightens image (maps dark pixels higher). γ > 1 darkens. γ=1 is identity. Current γ={gamma:.2f}")

        elif op == "Log transform (nonlinear)":
            c = st.slider("Constant c", 1, 50, 10)
            out = normalize_display(c * np.log1p(gray.astype(float)))
            st.image(out, caption=f"I_out = {c}×log(1+I_in)", use_container_width=True, clamp=True)

        elif op == "Negative image":
            out = 255 - gray
            st.image(out, caption="I_out = 255 - I_in", use_container_width=True, clamp=True)

        else:
            thresh = st.slider("Threshold value T", 0, 255, 127)
            _, out = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
            st.image(out, caption=f"I_out = 255 if I_in>{thresh} else 0", use_container_width=True, clamp=True)

# ── TAB 5: Image Statistics ───────────────────────────────────────────────────
with tab5:
    st.markdown("### Image Statistics & Histogram")
    theory_box("The histogram of an image shows the frequency of each intensity level. "
               "Mean measures average brightness. Standard deviation measures contrast. "
               "A well-distributed histogram indicates a well-exposed image.")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3))
    axes[0].imshow(gray, cmap="gray")
    axes[0].set_title("Grayscale Image"); axes[0].axis("off")
    hist = cv2.calcHist([gray], [0], None, [256], [0,256]).flatten()
    axes[1].bar(range(256), hist, color="#4f6ef7", width=1, alpha=0.85)
    axes[1].set_title("Histogram"); axes[1].set_xlabel("Intensity"); axes[1].set_ylabel("Frequency")
    axes[1].set_xlim([0,255])
    plt.tight_layout()
    fig_to_st(fig)

    metric_row([
        ("Mean intensity", f"{gray.mean():.1f}"),
        ("Std deviation",  f"{gray.std():.1f}"),
        ("Min value",      f"{gray.min()}"),
        ("Max value",      f"{gray.max()}"),
        ("Image size",     f"{gray.shape[1]}×{gray.shape[0]}"),
        ("Total pixels",   f"{gray.size:,}"),
    ])
