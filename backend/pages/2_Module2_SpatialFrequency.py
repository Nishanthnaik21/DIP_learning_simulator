import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from utils.helpers import *



page_header(2, "Spatial & Frequency Domain", "📡",
    "Apply histogram processing, spatial filters, and explore DFT-based frequency domain filtering.")

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
    img_rgb = upload_image("mod2")
    gray    = to_gray(img_rgb)

with tabs_container:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Histogram Processing",
        "🌊 Smoothing Filters",
        "🔪 Sharpening Filters",
        "📡 DFT Spectrum",
        "🎛️ Frequency Filters"
    ])

# ── TAB 1: Histogram Processing ───────────────────────────────────────────────
with tab1:
    st.markdown("### Histogram Processing")
    theory_box("Histogram Equalisation redistributes pixel intensities so the histogram is approximately flat, "
               "increasing global contrast. CLAHE (Contrast Limited AHE) applies equalisation in local tiles "
               "and clips the histogram to prevent over-amplification of noise.")

    method = st.radio("Method", ["Global Equalisation", "CLAHE (Adaptive)"], horizontal=True)

    if method == "Global Equalisation":
        eq = cv2.equalizeHist(gray)
    else:
        clip = st.slider("Clip limit", 1.0, 10.0, 2.0)
        tile = st.slider("Tile size", 2, 16, 8)
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
        eq = clahe.apply(gray)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    axes[0,0].imshow(gray, cmap="gray"); axes[0,0].set_title("Original"); axes[0,0].axis("off")
    axes[0,1].imshow(eq, cmap="gray");   axes[0,1].set_title("Enhanced"); axes[0,1].axis("off")
    h1 = cv2.calcHist([gray],[0],None,[256],[0,256]).flatten()
    h2 = cv2.calcHist([eq],  [0],None,[256],[0,256]).flatten()
    axes[1,0].bar(range(256),h1,color="#4f6ef7",width=1); axes[1,0].set_title("Original histogram")
    axes[1,1].bar(range(256),h2,color="#22c55e",width=1); axes[1,1].set_title("Enhanced histogram")
    plt.tight_layout(); fig_to_st(fig)
    metric_row([("Original mean",f"{gray.mean():.1f}"),("Enhanced mean",f"{eq.mean():.1f}"),
                ("Original std",f"{gray.std():.1f}"),("Enhanced std",f"{eq.std():.1f}"),
                ("PSNR",f"{psnr(gray,eq):.1f} dB")])

# ── TAB 2: Smoothing Filters ──────────────────────────────────────────────────
with tab2:
    st.markdown("### Smoothing Spatial Filters")
    theory_box("Smoothing filters reduce noise and detail by averaging or computing weighted averages of "
               "neighbouring pixels. Averaging blur is simple but blurs edges. Gaussian blur uses a "
               "bell-curve weighted kernel — more natural blur. Median filter replaces each pixel with "
               "the median of its neighbourhood — excellent for salt-and-pepper noise while preserving edges.")

    # Add noise option
    add_noise = st.checkbox("Add salt-and-pepper noise first")
    working = gray.copy()
    if add_noise:
        noise_prob = st.slider("Noise probability", 0.01, 0.2, 0.05)
        mask = np.random.rand(*gray.shape)
        working = gray.copy()
        working[mask < noise_prob/2] = 0
        working[mask > 1-noise_prob/2] = 255

    ftype = st.selectbox("Filter type", ["Average (Box) Filter","Gaussian Filter","Median Filter","Bilateral Filter"])
    ksize = st.slider("Kernel size", 3, 21, 5, step=2)

    if ftype == "Average (Box) Filter":
        out = cv2.blur(working, (ksize, ksize))
        theory_box(f"Box filter: each output pixel = average of {ksize}×{ksize} = {ksize*ksize} neighbours. Kernel = all 1/{ksize*ksize}")
    elif ftype == "Gaussian Filter":
        sigma = st.slider("Sigma (σ)", 0.5, 10.0, 1.5)
        out = cv2.GaussianBlur(working, (ksize, ksize), sigma)
        theory_box(f"Gaussian kernel: G(x,y) = e^(-(x²+y²)/(2σ²)) / (2πσ²). σ={sigma:.1f} controls spread.")
    elif ftype == "Median Filter":
        out = cv2.medianBlur(working, ksize)
        theory_box(f"Median filter: replaces pixel with median of its {ksize}×{ksize} neighbourhood. Non-linear — preserves edges, kills salt-and-pepper.")
    else:
        d = st.slider("Diameter", 3, 15, 9, step=2)
        sc = st.slider("Sigma colour", 10, 150, 75)
        ss = st.slider("Sigma space", 10, 150, 75)
        out = cv2.bilateralFilter(working.astype(np.uint8), d, sc, ss)
        theory_box("Bilateral filter: smooths while preserving edges by weighing neighbours by both spatial distance AND intensity similarity.")

    show_images([(working,"Input (with noise if enabled)"),(out,f"{ftype} output")], n_cols=2)
    metric_row([("PSNR vs original",f"{psnr(gray,out):.1f} dB"),
                ("Mean diff",f"{abs(gray.astype(int)-out.astype(int)).mean():.2f}"),
                ("Kernel size",f"{ksize}×{ksize}")])

# ── TAB 3: Sharpening Filters ─────────────────────────────────────────────────
with tab3:
    st.markdown("### Sharpening Spatial Filters")
    theory_box("Sharpening filters enhance edges by subtracting a blurred version or by adding high-frequency "
               "components back to the image. The Laplacian operator computes the second derivative "
               "of intensity — zero in smooth regions, large at edges. Unsharp masking = original + α × (original − blurred).")

    stype = st.selectbox("Sharpening method", [
        "Laplacian sharpening","Unsharp masking","Sobel edge enhancement","High-boost filtering"])

    c1, c2 = st.columns(2)
    with c1:
        st.image(gray, caption="Original", use_container_width=True, clamp=True)

    with c2:
        if stype == "Laplacian sharpening":
            lap = cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F)
            w = st.slider("Sharpening weight", 0.0, 2.0, 1.0)
            out = np.clip(gray.astype(float) - w * lap, 0, 255).astype(np.uint8)
            st.image(out, caption=f"Laplacian sharpened (w={w})", use_container_width=True, clamp=True)
            theory_box("∇²f detects intensity changes in all directions. Subtracting it from original enhances edges.")

        elif stype == "Unsharp masking":
            sigma = st.slider("Blur sigma", 0.5, 5.0, 2.0)
            amount = st.slider("Amount (α)", 0.0, 3.0, 1.5)
            blurred = cv2.GaussianBlur(gray, (0,0), sigma)
            out = np.clip(gray.astype(float) + amount*(gray.astype(float)-blurred.astype(float)), 0, 255).astype(np.uint8)
            st.image(out, caption=f"Unsharp mask (α={amount})", use_container_width=True, clamp=True)
            theory_box(f"Sharpened = Original + {amount:.1f} × (Original − Gaussian blur). Mask = high-frequency detail.")

        elif stype == "Sobel edge enhancement":
            ksize = st.select_slider("Kernel size", [1,3,5,7], 3)
            sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=ksize)
            sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=ksize)
            mag = np.sqrt(sx**2 + sy**2)
            w = st.slider("Edge weight", 0.0, 2.0, 0.5)
            out = np.clip(gray.astype(float) + w * mag, 0, 255).astype(np.uint8)
            st.image(out, caption="Sobel enhanced", use_container_width=True, clamp=True)

        else:
            k = st.slider("Boost factor (k)", 1.0, 5.0, 2.0)
            blurred = cv2.GaussianBlur(gray, (0,0), 3)
            out = np.clip(k * gray.astype(float) - (k-1) * blurred.astype(float), 0, 255).astype(np.uint8)
            st.image(out, caption=f"High-boost (k={k})", use_container_width=True, clamp=True)
            theory_box(f"High-boost: k×f - (k-1)×f_blurred. When k=1, same as unsharp masking. k>{k:.0f} = stronger boost.")

# ── TAB 4: DFT Spectrum ────────────────────────────────────────────────────────
with tab4:
    st.markdown("### Discrete Fourier Transform (DFT)")
    theory_box("The 2D DFT transforms an image from the spatial domain (pixels) to the frequency domain. "
               "The magnitude spectrum shows which frequencies are present. Low frequencies (centre of shifted "
               "spectrum) = large smooth regions. High frequencies (edges) = fine detail and noise. "
               "Shifting the zero-frequency to centre makes the spectrum easier to interpret.")

    f = np.fft.fft2(gray.astype(float))
    fshift = np.fft.fftshift(f)
    magnitude = 20 * np.log(np.abs(fshift) + 1)
    phase = np.angle(fshift)

    view = st.radio("Spectrum view", ["Magnitude","Phase","Both"], horizontal=True)

    fig, axes = plt.subplots(1, 3 if view=="Both" else 2, figsize=(12 if view=="Both" else 8, 4))
    ax = axes if view != "Both" else axes
    ax[0].imshow(gray, cmap="gray"); ax[0].set_title("Spatial domain"); ax[0].axis("off")

    if view in ("Magnitude","Both"):
        idx = 1 if view != "Both" else 1
        ax[idx].imshow(magnitude, cmap="inferno"); ax[idx].set_title("Magnitude spectrum (log)"); ax[idx].axis("off")
    if view in ("Phase","Both"):
        idx = 1 if view=="Phase" else 2
        ax[idx].imshow(phase, cmap="twilight"); ax[idx].set_title("Phase spectrum"); ax[idx].axis("off")

    plt.tight_layout(); fig_to_st(fig)
    st.caption("Bright centre = dominant low frequencies (smooth background). Bright radial lines = dominant orientations (edges).")

    if st.checkbox("Show 1D frequency profile (horizontal centre row)"):
        row = magnitude[magnitude.shape[0]//2, :]
        fig2, ax2 = plt.subplots(figsize=(8,2))
        ax2.plot(row, color="#4f6ef7"); ax2.set_title("Horizontal frequency profile")
        ax2.set_xlabel("Frequency"); ax2.set_ylabel("Log magnitude")
        plt.tight_layout(); fig_to_st(fig2)

# ── TAB 5: Frequency Filters ──────────────────────────────────────────────────
with tab5:
    st.markdown("### Frequency Domain Filtering")
    theory_box("Filtering in the frequency domain: (1) compute DFT, (2) multiply by a filter mask, "
               "(3) compute inverse DFT. Low-pass filter keeps low frequencies → smoothing. "
               "High-pass filter keeps high frequencies → edge enhancement. "
               "Band-pass/notch filters target specific frequency bands.")

    ftype2 = st.selectbox("Filter type", [
        "Ideal Low-pass","Ideal High-pass",
        "Gaussian Low-pass","Gaussian High-pass",
        "Butterworth Low-pass","Butterworth High-pass"
    ])
    D0 = st.slider("Cut-off frequency D₀ (radius)", 5, min(gray.shape)//2, 30)

    rows, cols = gray.shape
    crow, ccol = rows//2, cols//2
    Y, X = np.ogrid[:rows, :cols]
    D = np.sqrt((Y - crow)**2 + (X - ccol)**2)

    if ftype2 == "Ideal Low-pass":
        H = (D <= D0).astype(float)
        theory_box(f"Ideal LPF: H(u,v) = 1 if D(u,v) ≤ {D0}, else 0. Causes ringing (Gibbs effect) due to sharp cutoff.")
    elif ftype2 == "Ideal High-pass":
        H = (D > D0).astype(float)
        theory_box(f"Ideal HPF: H(u,v) = 1 if D(u,v) > {D0}, else 0. Removes smooth background, keeps edges.")
    elif ftype2 == "Gaussian Low-pass":
        H = np.exp(-(D**2) / (2*D0**2))
        theory_box(f"GLPF: H(u,v) = e^(-D²/2D₀²). No ringing. D₀={D0} controls cutoff smoothness.")
    elif ftype2 == "Gaussian High-pass":
        H = 1 - np.exp(-(D**2) / (2*D0**2))
        theory_box(f"GHPF: H(u,v) = 1 - e^(-D²/2D₀²). Smooth transition, preserves edge detail.")
    elif ftype2 == "Butterworth Low-pass":
        n = st.slider("Order n", 1, 10, 2)
        H = 1 / (1 + (D/D0)**(2*n))
        theory_box(f"BLPF: H = 1/(1+(D/D₀)^2n). Order n={n} controls sharpness of transition band.")
    else:
        n = st.slider("Order n", 1, 10, 2)
        H = 1 - 1/(1 + (D/D0)**(2*n))
        theory_box(f"BHPF: H = 1 - 1/(1+(D/D₀)^2n). Order n={n}.")

    F = np.fft.fftshift(np.fft.fft2(gray.astype(float)))
    G = F * H
    g = np.abs(np.fft.ifft2(np.fft.ifftshift(G)))

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(gray, cmap="gray"); axes[0].set_title("Original"); axes[0].axis("off")
    axes[1].imshow(H, cmap="gray"); axes[1].set_title(f"Filter mask H (D₀={D0})"); axes[1].axis("off")
    axes[2].imshow(normalize_display(g), cmap="gray"); axes[2].set_title("Filtered result"); axes[2].axis("off")
    plt.tight_layout(); fig_to_st(fig)
    metric_row([("PSNR",f"{psnr(gray, normalize_display(g)):.1f} dB"),
                ("Cutoff D₀",str(D0)),("Filter",ftype2)])
