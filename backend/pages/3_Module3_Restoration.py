import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
from utils.helpers import *



page_header(3, "Image Restoration", "🔧",
    "Add degradation and noise to images, then restore them using Wiener, inverse, and constrained least squares filtering.")

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
    img_rgb = upload_image("mod3")
    gray    = to_gray(img_rgb).astype(np.float64)

with tabs_container:
    tab1, tab2, tab3, tab4 = st.tabs([
    "💥 Noise Models",
    "🔄 Inverse Filtering",
    "🧠 Wiener Filtering",
    "📏 Constrained LS & Metrics"
])

def add_noise_to(img, noise_type, **kw):
    out = img.copy().astype(float)
    if noise_type == "Gaussian":
        sigma = kw.get("sigma",20)
        out += np.random.normal(0, sigma, img.shape)
    elif noise_type == "Salt & Pepper":
        prob = kw.get("prob",0.05)
        mask = np.random.rand(*img.shape)
        out[mask < prob/2] = 0
        out[mask > 1-prob/2] = 255
    elif noise_type == "Rayleigh":
        sigma = kw.get("sigma",20)
        out += np.random.rayleigh(sigma, img.shape)
    elif noise_type == "Uniform":
        a = kw.get("a",30)
        out += np.random.uniform(-a, a, img.shape)
    elif noise_type == "Erlang (Gamma)":
        k = kw.get("k",2); scale = kw.get("scale",10)
        out += np.random.gamma(k, scale, img.shape)
    return np.clip(out, 0, 255).astype(np.uint8)

def motion_blur_psf(size=15, angle=0):
    psf = np.zeros((size, size))
    psf[size//2, :] = 1.0 / size
    M = cv2.getRotationMatrix2D((size//2, size//2), angle, 1)
    psf = cv2.warpAffine(psf, M, (size, size))
    return psf / psf.sum()

# ── TAB 1: Noise Models ────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Noise Models")
    theory_box("Real images are corrupted by various noise types during acquisition and transmission. "
               "Gaussian: electronic sensor noise (symmetric, bell-curve). "
               "Salt & Pepper: impulse noise from transmission errors (random black/white pixels). "
               "Rayleigh/Gamma: occur in radar and ultrasound imaging.")

    ntype = st.selectbox("Noise type", ["Gaussian","Salt & Pepper","Rayleigh","Uniform","Erlang (Gamma)"])

    c1, c2 = st.columns(2)
    with c1:
        if ntype == "Gaussian":
            sigma = st.slider("Sigma (noise strength)", 1, 80, 20)
            noisy = add_noise_to(gray, "Gaussian", sigma=sigma)
        elif ntype == "Salt & Pepper":
            prob = st.slider("Probability", 0.01, 0.3, 0.05)
            noisy = add_noise_to(gray, "Salt & Pepper", prob=prob)
        elif ntype == "Rayleigh":
            sigma = st.slider("Sigma", 5, 60, 20)
            noisy = add_noise_to(gray, "Rayleigh", sigma=sigma)
        elif ntype == "Uniform":
            a = st.slider("Range ±a", 5, 80, 30)
            noisy = add_noise_to(gray, "Uniform", a=a)
        else:
            k = st.slider("Shape k", 1, 5, 2)
            scale = st.slider("Scale", 5, 40, 10)
            noisy = add_noise_to(gray, "Erlang (Gamma)", k=k, scale=scale)

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    axes[0,0].imshow(gray, cmap="gray"); axes[0,0].set_title("Original"); axes[0,0].axis("off")
    axes[0,1].imshow(noisy, cmap="gray"); axes[0,1].set_title(f"{ntype} noise"); axes[0,1].axis("off")
    h1 = cv2.calcHist([gray.astype(np.uint8)],[0],None,[256],[0,256]).flatten()
    h2 = cv2.calcHist([noisy],[0],None,[256],[0,256]).flatten()
    axes[1,0].bar(range(256),h1,width=1,color="#4f6ef7"); axes[1,0].set_title("Original histogram")
    axes[1,1].bar(range(256),h2,width=1,color="#ef4444"); axes[1,1].set_title(f"{ntype} noise histogram")
    plt.tight_layout(); fig_to_st(fig)
    metric_row([("PSNR",f"{psnr(gray.astype(np.uint8),noisy):.1f} dB"),
                ("Noise mean",f"{(noisy.astype(float)-gray).mean():.2f}"),
                ("Noise std",f"{(noisy.astype(float)-gray).std():.2f}")])

# ── TAB 2: Inverse Filtering ──────────────────────────────────────────────────
with tab2:
    st.markdown("### Inverse Filtering")
    theory_box("If a degradation function H is known, inverse filtering applies H⁻¹ to recover the original. "
               "Problem: dividing by small H values amplifies noise catastrophically. "
               "Truncated inverse filtering clips H values below a threshold to control noise amplification.")

    blur_size = st.slider("Motion blur size (PSF)", 3, 25, 10, step=2)
    angle     = st.slider("Blur angle (degrees)", 0, 180, 0)
    noise_lvl = st.slider("Additive Gaussian noise σ", 0, 30, 5)

    psf = motion_blur_psf(blur_size, angle)
    psf_pad = np.zeros_like(gray)
    ph, pw = psf.shape
    psf_pad[:ph,:pw] = psf

    H = np.fft.fft2(psf_pad)
    F = np.fft.fft2(gray)
    G = H * F
    if noise_lvl > 0:
        G += np.fft.fft2(np.random.normal(0, noise_lvl, gray.shape))

    degraded = np.abs(np.fft.ifft2(G))

    threshold = st.slider("Inverse filter threshold (clip |H| below this)", 0.001, 0.5, 0.05, step=0.005)
    H_inv = np.where(np.abs(H) > threshold, 1.0/H, 0)
    restored = np.abs(np.fft.ifft2(np.fft.fft2(degraded) * H_inv))

    show_images([
        (normalize_display(gray),"Original"),
        (normalize_display(degraded),f"Degraded (blur={blur_size}, noise={noise_lvl})"),
        (normalize_display(restored),f"Inverse filtered (thr={threshold})")
    ], n_cols=3)
    metric_row([("Degraded PSNR",f"{psnr(gray.astype(np.uint8),normalize_display(degraded)):.1f} dB"),
                ("Restored PSNR",f"{psnr(gray.astype(np.uint8),normalize_display(restored)):.1f} dB")])
    theory_box(f"Threshold={threshold}: |H| values below this are set to 0 in inverse filter to avoid noise explosion.")

# ── TAB 3: Wiener Filtering ────────────────────────────────────────────────────
with tab3:
    st.markdown("### Wiener Filtering (Minimum Mean Square Error)")
    theory_box("Wiener filter minimises the mean square error between the restored and original image. "
               "It balances between inverse filtering (when signal >> noise) and doing nothing (when noise >> signal). "
               "Formula: Ĥ_w = H* / (|H|² + K), where K = noise-to-signal power ratio. "
               "When K=0, Wiener = pure inverse filter. As K increases, less noise amplification.")

    blur_size2 = st.slider("Motion blur size", 3, 25, 10, step=2, key="wsz")
    angle2     = st.slider("Blur angle", 0, 180, 0, key="wang")
    noise_lvl2 = st.slider("Noise σ", 0, 50, 10, key="wn")
    K          = st.slider("K (noise/signal ratio)", 0.0001, 0.5, 0.01, step=0.0005, format="%.4f")

    psf2 = motion_blur_psf(blur_size2, angle2)
    psf_pad2 = np.zeros_like(gray)
    ph2,pw2 = psf2.shape
    psf_pad2[:ph2,:pw2] = psf2
    H2  = np.fft.fft2(psf_pad2)
    F2  = np.fft.fft2(gray)
    G2  = H2 * F2
    if noise_lvl2 > 0:
        G2 += np.fft.fft2(np.random.normal(0, noise_lvl2, gray.shape))
    degraded2 = np.real(np.fft.ifft2(G2))

    H_conj = np.conj(H2)
    H_w    = H_conj / (np.abs(H2)**2 + K)
    restored2 = np.real(np.fft.ifft2(H_w * np.fft.fft2(degraded2)))

    show_images([
        (normalize_display(gray),"Original"),
        (normalize_display(degraded2),f"Degraded"),
        (normalize_display(restored2),f"Wiener restored (K={K:.4f})")
    ], n_cols=3)
    metric_row([("Degraded PSNR",f"{psnr(gray.astype(np.uint8),normalize_display(degraded2)):.1f} dB"),
                ("Wiener PSNR",  f"{psnr(gray.astype(np.uint8),normalize_display(restored2)):.1f} dB"),
                ("K value",f"{K:.4f}")])

    theory_box(f"K={K:.4f}. Low K → trust the inverse filter more (better when little noise). "
               "High K → regularise more aggressively (better when noise is strong).")

# ── TAB 4: Constrained LS & Metrics ───────────────────────────────────────────
with tab4:
    st.markdown("### Constrained Least Squares Filtering & Quality Metrics")
    theory_box("Constrained Least Squares (CLS) filtering minimises the Laplacian energy of the restored image "
               "subject to the constraint that the restoration fits the degraded image. "
               "Formula: F̂ = H* / (|H|² + γ|P|²) where P is the Laplacian filter in frequency domain. "
               "γ is the regularisation parameter that controls smoothness vs data fidelity.")

    blur_size3 = st.slider("Blur size", 3, 20, 8, step=2, key="clsz")
    noise_lvl3 = st.slider("Noise σ", 0, 50, 15, key="cln")
    gamma      = st.slider("γ (regularisation)", 0.0001, 1.0, 0.01, step=0.001, format="%.4f")

    psf3 = motion_blur_psf(blur_size3, 0)
    psf_pad3 = np.zeros_like(gray); psf_pad3[:psf3.shape[0],:psf3.shape[1]] = psf3
    H3 = np.fft.fft2(psf_pad3)
    G3 = H3 * np.fft.fft2(gray)
    if noise_lvl3 > 0:
        G3 += np.fft.fft2(np.random.normal(0, noise_lvl3, gray.shape))
    degraded3 = np.real(np.fft.ifft2(G3))

    # Laplacian in frequency domain
    lap = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=float)
    lap_pad = np.zeros_like(gray); lap_pad[:3,:3] = lap
    P = np.fft.fft2(lap_pad)

    H3_conj = np.conj(H3)
    H_cls   = H3_conj / (np.abs(H3)**2 + gamma * np.abs(P)**2)
    restored3 = np.real(np.fft.ifft2(H_cls * np.fft.fft2(degraded3)))

    show_images([
        (normalize_display(gray),"Original"),
        (normalize_display(degraded3),"Degraded"),
        (normalize_display(restored3),f"CLS restored (γ={gamma:.4f})")
    ], n_cols=3)

    orig_u8     = gray.astype(np.uint8)
    degraded_u8 = normalize_display(degraded3)
    restored_u8 = normalize_display(restored3)

    deg_psnr  = psnr(orig_u8, degraded_u8)
    rest_psnr = psnr(orig_u8, restored_u8)

    def ssim_simple(a, b):
        a, b = a.astype(float), b.astype(float)
        mu1, mu2 = a.mean(), b.mean()
        s1, s2, s12 = a.std(), b.std(), np.cov(a.flatten(), b.flatten())[0,1]
        c1, c2 = (0.01*255)**2, (0.03*255)**2
        return ((2*mu1*mu2+c1)*(2*s12+c2)) / ((mu1**2+mu2**2+c1)*(s1**2+s2**2+c2))

    metric_row([
        ("Degraded PSNR",  f"{deg_psnr:.1f} dB"),
        ("CLS PSNR",       f"{rest_psnr:.1f} dB"),
        ("Degraded SSIM",  f"{ssim_simple(orig_u8,degraded_u8):.3f}"),
        ("CLS SSIM",       f"{ssim_simple(orig_u8,restored_u8):.3f}"),
        ("PSNR gain",      f"+{rest_psnr-deg_psnr:.1f} dB"),
    ])
    theory_box("PSNR (Peak Signal-to-Noise Ratio): higher = better quality. "
               "SSIM (Structural Similarity Index): 1.0 = identical, 0 = no similarity. "
               "Both measure how close the restored image is to the original.")
