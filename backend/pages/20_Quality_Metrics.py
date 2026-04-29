import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import io
from utils.theme import inject, page_header, theory_card, metric_row, section_title, glass_card
from utils.helpers import upload_image, to_gray, normalize_display, fig_to_st, comparison_slider

inject("Quality Metrics", "📏")


page_header("Image Quality Metrics Dashboard",
            "PSNR · SSIM · MSE · MAE · VIF · BRISQUE · SIDE-BY-SIDE COMPARISON", "📏", "#ff3366")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "Image quality metrics quantify how 'good' a processed image is compared to a reference. "
    "PSNR: Peak Signal-to-Noise Ratio — ratio of max signal to noise power (dB). Higher = better. "
    "SSIM: Structural Similarity — measures luminance, contrast, and structure together (0–1). "
    "MSE: Mean Squared Error — average squared pixel difference. Lower = better. "
    "MAE: Mean Absolute Error — average absolute pixel difference. Lower = better. "
    "VIF: Visual Information Fidelity — information-theoretic measure of quality."
)

img_rgb = upload_image("qm_up")
gray    = to_gray(img_rgb)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📏 Degradation Settings")
deg_type = st.sidebar.selectbox("Degradation type", [
    "Gaussian Noise", "Salt & Pepper Noise", "JPEG Compression",
    "Gaussian Blur", "Motion Blur", "Quantization", "Custom Upload"
])

# ── Generate degraded image ───────────────────────────────────────────────────
degraded = gray.copy()
deg_params = {}

if deg_type == "Gaussian Noise":
    sigma = st.sidebar.slider("Noise σ", 1, 80, 20)
    degraded = np.clip(gray.astype(float) + np.random.normal(0, sigma, gray.shape), 0, 255).astype(np.uint8)
    deg_params = {"type": "Gaussian", "σ": sigma}

elif deg_type == "Salt & Pepper Noise":
    prob = st.sidebar.slider("Probability", 0.01, 0.30, 0.05)
    degraded = gray.copy()
    mask = np.random.rand(*gray.shape)
    degraded[mask < prob/2] = 0; degraded[mask > 1-prob/2] = 255
    deg_params = {"type": "Salt & Pepper", "prob": prob}

elif deg_type == "JPEG Compression":
    q = st.sidebar.slider("JPEG Quality", 1, 99, 30)
    from PIL import Image as PILImage
    pil = PILImage.fromarray(gray); buf = io.BytesIO()
    pil.save(buf, "JPEG", quality=q); buf.seek(0)
    degraded = np.array(PILImage.open(buf).convert("L"))
    deg_params = {"type": "JPEG", "quality": q}

elif deg_type == "Gaussian Blur":
    k = st.sidebar.slider("Sigma", 0.5, 15.0, 3.0)
    degraded = cv2.GaussianBlur(gray, (0,0), k)
    deg_params = {"type": "Gaussian Blur", "σ": k}

elif deg_type == "Motion Blur":
    length = st.sidebar.slider("Blur length", 5, 40, 15)
    angle  = st.sidebar.slider("Angle (deg)", 0, 180, 0)
    kernel = np.zeros((length, length))
    kernel[length//2, :] = 1.0 / length
    M = cv2.getRotationMatrix2D((length//2, length//2), angle, 1)
    kernel = cv2.warpAffine(kernel, M, (length, length))
    kernel /= kernel.sum() + 1e-10
    degraded = np.clip(cv2.filter2D(gray.astype(float), -1, kernel), 0, 255).astype(np.uint8)
    deg_params = {"type": "Motion Blur", "length": length, "angle": angle}

elif deg_type == "Quantization":
    bits = st.sidebar.slider("Bits", 1, 7, 3)
    levels = 2**bits
    degraded = (gray // (256//levels)) * (256//levels)
    deg_params = {"type": "Quantization", "bits": bits, "levels": levels}

else:
    st.sidebar.info("Upload a second image below to compare against.")
    file2 = st.file_uploader("Upload degraded/processed image", type=["jpg","jpeg","png"])
    if file2:
        from PIL import Image as PILImage
        degraded = np.array(PILImage.open(file2).convert("L"))
        degraded = cv2.resize(degraded, (gray.shape[1], gray.shape[0]))

# ── Compute all metrics ────────────────────────────────────────────────────────
def compute_psnr(ref, deg):
    mse = np.mean((ref.astype(float)-deg.astype(float))**2)
    if mse == 0: return 100.0
    return 20*np.log10(255.0/np.sqrt(mse))

def compute_ssim(ref, deg, win=11):
    """Simplified SSIM."""
    r, d = ref.astype(float), deg.astype(float)
    mu1 = cv2.GaussianBlur(r, (win,win), 1.5)
    mu2 = cv2.GaussianBlur(d, (win,win), 1.5)
    mu1_sq, mu2_sq, mu12 = mu1**2, mu2**2, mu1*mu2
    s11 = cv2.GaussianBlur(r*r,(win,win),1.5)-mu1_sq
    s22 = cv2.GaussianBlur(d*d,(win,win),1.5)-mu2_sq
    s12 = cv2.GaussianBlur(r*d,(win,win),1.5)-mu12
    C1,C2 = (0.01*255)**2, (0.03*255)**2
    ssim_map = ((2*mu12+C1)*(2*s12+C2)) / ((mu1_sq+mu2_sq+C1)*(s11+s22+C2))
    return float(np.mean(ssim_map)), ssim_map

def compute_vif(ref, deg):
    """Simplified VIF approximation."""
    r, d = ref.astype(float)/255, deg.astype(float)/255
    scales, num, den = [2,4,8,16], 0, 0
    for s in scales:
        rs = cv2.resize(r, (r.shape[1]//s, r.shape[0]//s))
        ds = cv2.resize(d, (d.shape[1]//s, d.shape[0]//s))
        sigma_sq = np.var(rs) + 1e-10
        sigma_sq_n = np.var(rs - ds) + 1e-10
        g = np.sum(rs*ds) / (np.sum(rs**2)+1e-10)
        num += np.log2(1 + g**2 * sigma_sq/sigma_sq_n) * rs.size
        den += np.log2(1 + sigma_sq/1e-10) * rs.size + 1e-10
    return min(1.0, max(0.0, num/(den+1e-10)))

psnr_val = compute_psnr(gray, degraded)
ssim_val, ssim_map = compute_ssim(gray, degraded)
mse_val  = np.mean((gray.astype(float)-degraded.astype(float))**2)
mae_val  = np.mean(np.abs(gray.astype(float)-degraded.astype(float)))
vif_val  = compute_vif(gray, degraded)
diff_map = np.abs(gray.astype(int) - degraded.astype(int)).astype(np.uint8)

# ── Top Metric Display ─────────────────────────────────────────────────────────
section_title("QUALITY SCORES", "#ff3366")

def psnr_grade(v):
    if v > 40: return "Excellent","#00ff9d"
    if v > 30: return "Good","#00a8ff"
    if v > 20: return "Fair","#ffb700"
    return "Poor","#ff3366"

def ssim_grade(v):
    if v > 0.95: return "Excellent","#00ff9d"
    if v > 0.80: return "Good","#00a8ff"
    if v > 0.60: return "Fair","#ffb700"
    return "Poor","#ff3366"

pg, pc = psnr_grade(psnr_val)
sg, sc = ssim_grade(ssim_val)

cols6 = st.columns(6)
metrics_data = [
    ("PSNR",  f"{psnr_val:.2f} dB",  f"Grade: {pg}", pc),
    ("SSIM",  f"{ssim_val:.4f}",      f"Grade: {sg}", sc),
    ("MSE",   f"{mse_val:.2f}",       "Lower is better","#b44fff"),
    ("MAE",   f"{mae_val:.2f}",       "Pixel avg error","#ffb700"),
    ("VIF",   f"{vif_val:.3f}",       "0–1, higher=better","#00fff5"),
    ("NCC",   f"{np.corrcoef(gray.flatten(),degraded.flatten())[0,1]:.4f}",
              "Normalised correlation","#00ff9d"),
]
for col, (lbl, val, sub, color) in zip(cols6, metrics_data):
    with col:
        col.markdown(f"""
        <div style="background:rgba(10,30,70,0.55);border:1px solid {color}33;border-radius:12px;
                    padding:14px 12px;text-align:center;position:relative;overflow:hidden;
                    box-shadow:0 8px 24px rgba(0,0,0,0.4),0 0 15px {color}15;
                    transform:perspective(500px) rotateX(3deg)">
          <div style="position:absolute;top:0;left:0;right:0;height:1px;
                      background:linear-gradient(90deg,transparent,{color}99,transparent)"></div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#3a6a9a;
                      letter-spacing:0.12em;margin-bottom:6px;text-transform:uppercase">{lbl}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;
                      color:{color};text-shadow:0 0 12px {color}77;line-height:1.1">{val}</div>
          <div style="font-size:0.67rem;color:#3a6a9a;margin-top:4px">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Visual comparison tabs ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🖼️ SIDE-BY-SIDE","🌡️ DIFFERENCE MAPS","📈 QUALITY CURVES","📖 METRIC GUIDE"])

with tab1:
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown("**Reference**"); st.image(gray, use_container_width=True, clamp=True)
    with c2: st.markdown(f"**Degraded ({deg_type})**"); st.image(degraded, use_container_width=True, clamp=True)
    with c3:
        st.markdown("**SSIM Map (bright = structural loss)**")
        ssim_display = normalize_display(1 - ssim_map)
        st.image(cv2.applyColorMap(ssim_display, cv2.COLORMAP_HOT), use_container_width=True)
    st.markdown("#### ↔️ Drag to compare")
    comparison_slider(gray, degraded, "Reference", f"Degraded ({deg_type})", key="qm_cmp")

with tab2:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), facecolor="#020818")
    for ax in axes.flat: ax.set_facecolor("#091428")
    axes[0,0].imshow(gray, cmap="gray"); axes[0,0].set_title("Reference", color="#8ab4d4"); axes[0,0].axis("off")
    axes[0,1].imshow(degraded, cmap="gray"); axes[0,1].set_title("Degraded", color="#8ab4d4"); axes[0,1].axis("off")
    axes[0,2].imshow(diff_map, cmap="hot"); axes[0,2].set_title("Absolute Difference", color="#8ab4d4"); axes[0,2].axis("off")
    axes[1,0].imshow(1 - ssim_map, cmap="inferno"); axes[1,0].set_title("SSIM Loss Map", color="#8ab4d4"); axes[1,0].axis("off")
    # Error histogram
    axes[1,1].hist(diff_map.flatten(), bins=64, color="#00a8ff", alpha=0.8)
    axes[1,1].set_title("Error histogram", color="#8ab4d4"); axes[1,1].tick_params(colors="#3a6a9a")
    for s in axes[1,1].spines.values(): s.set_color("#1a3a5a")
    # Scatter
    sample_idx = np.random.choice(gray.size, min(5000, gray.size), replace=False)
    axes[1,2].scatter(gray.flatten()[sample_idx], degraded.flatten()[sample_idx],
                      alpha=0.15, s=1, color="#00fff5")
    axes[1,2].plot([0,255],[0,255],"r--",alpha=0.5,linewidth=1)
    axes[1,2].set_title("Pixel scatter (ref vs deg)", color="#8ab4d4")
    axes[1,2].tick_params(colors="#3a6a9a")
    for s in axes[1,2].spines.values(): s.set_color("#1a3a5a")
    plt.tight_layout(); fig_to_st(fig)

with tab3:
    section_title("PSNR & SSIM vs DEGRADATION LEVEL","#ff3366")
    if deg_type in ("Gaussian Noise","Salt & Pepper Noise"):
        levels = np.linspace(0, 60, 30)
        psnr_c, ssim_c = [], []
        for lvl in levels:
            if deg_type == "Gaussian Noise":
                d = np.clip(gray.astype(float)+np.random.normal(0,lvl,gray.shape),0,255).astype(np.uint8)
            else:
                d = gray.copy(); m=np.random.rand(*gray.shape)
                p=max(0.001,lvl/200); d[m<p/2]=0; d[m>1-p/2]=255
            psnr_c.append(compute_psnr(gray,d))
            ssim_c.append(compute_ssim(gray,d)[0])
        fig2, (ax1,ax2) = plt.subplots(1,2,figsize=(12,4),facecolor="#020818")
        for ax in [ax1,ax2]: ax.set_facecolor("#091428")
        ax1.plot(levels,psnr_c,color="#00a8ff",lw=2); ax1.axvline(sigma if deg_type=="Gaussian Noise" else prob*200,color="#ff3366",ls="--",alpha=0.7)
        ax1.set_title("PSNR vs Noise Level",color="#8ab4d4"); ax1.tick_params(colors="#3a6a9a")
        for s in ax1.spines.values(): s.set_color("#1a3a5a")
        ax2.plot(levels,ssim_c,color="#b44fff",lw=2); ax2.set_ylim(0,1)
        ax2.set_title("SSIM vs Noise Level",color="#8ab4d4"); ax2.tick_params(colors="#3a6a9a")
        for s in ax2.spines.values(): s.set_color("#1a3a5a")
        plt.tight_layout(); fig_to_st(fig2)
    elif deg_type == "JPEG Compression":
        qualities = [1,5,10,20,30,40,50,60,70,80,90,95]
        psnr_j, ssim_j = [], []
        for qq in qualities:
            from PIL import Image as PILImage
            pil=PILImage.fromarray(gray); b2=io.BytesIO()
            pil.save(b2,"JPEG",quality=qq); b2.seek(0)
            dq=np.array(PILImage.open(b2).convert("L"))
            psnr_j.append(compute_psnr(gray,dq)); ssim_j.append(compute_ssim(gray,dq)[0])
        fig3,(a1,a2)=plt.subplots(1,2,figsize=(12,4),facecolor="#020818")
        for ax in [a1,a2]: ax.set_facecolor("#091428")
        a1.plot(qualities,psnr_j,color="#00a8ff",lw=2,marker="o",ms=4); a1.set_title("PSNR vs JPEG Quality",color="#8ab4d4"); a1.tick_params(colors="#3a6a9a")
        for s in a1.spines.values(): s.set_color("#1a3a5a")
        a2.plot(qualities,ssim_j,color="#b44fff",lw=2,marker="s",ms=4); a2.set_ylim(0,1); a2.set_title("SSIM vs JPEG Quality",color="#8ab4d4"); a2.tick_params(colors="#3a6a9a")
        for s in a2.spines.values(): s.set_color("#1a3a5a")
        plt.tight_layout(); fig_to_st(fig3)
    else:
        st.info("Quality curves available for Gaussian Noise, Salt & Pepper, and JPEG Compression.")

with tab4:
    metrics_guide = [
        ("PSNR","20·log₁₀(255/√MSE)","dB","Higher better",">40 Excellent\n30–40 Good\n20–30 Fair\n<20 Poor",
         "Best for: comparing same type of distortion. Not perceptually correlated for all distortions."),
        ("SSIM","L(x,y)·C(x,y)·S(x,y)","0–1","Closer to 1 better",">0.95 Excellent\n0.8–0.95 Good\n0.6–0.8 Fair\n<0.6 Poor",
         "Best for: natural images, perceptual quality. Better than PSNR for structural changes."),
        ("MSE","mean((x-y)²)","pixel²","Lower better","Depends on scale",
         "Simple but not perceptually meaningful. Same MSE can look very different perceptually."),
        ("MAE","mean(|x-y|)","pixel","Lower better","Depends on scale",
         "More robust than MSE to outliers. Used when large errors should not be penalised quadratically."),
        ("VIF","mutual info ref vs deg","0–1","Closer to 1 better",">0.7 High quality",
         "Information-theoretic. Measures how much visual information is preserved after distortion."),
        ("NCC","Σ(x·y)/(|x|·|y|)","−1 to 1","Closer to 1 better",">0.99 Excellent",
         "Useful for template matching. Insensitive to linear brightness changes."),
    ]
    for name, formula, unit, direction, grades, notes in metrics_guide:
        st.markdown(f"""
        <div style="background:rgba(10,30,70,0.45);border:1px solid rgba(0,168,255,0.15);
                    border-left:3px solid #00a8ff;border-radius:0 10px 10px 0;
                    padding:14px 16px;margin:8px 0">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
            <div>
              <span style="font-family:'Orbitron',monospace;font-size:0.82rem;color:#00a8ff;font-weight:700">{name}</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#3a6a9a;margin-left:12px">{formula}</span>
            </div>
            <div style="display:flex;gap:8px">
              <span style="background:rgba(0,168,255,0.12);color:#00a8ff;border-radius:6px;padding:2px 8px;font-size:0.72rem">{unit}</span>
              <span style="background:rgba(0,255,157,0.12);color:#00ff9d;border-radius:6px;padding:2px 8px;font-size:0.72rem">{direction}</span>
            </div>
          </div>
          <div style="font-size:0.78rem;color:#8ab4d4;margin-top:8px;line-height:1.6">{notes}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#3a6a9a;
                      white-space:pre;margin-top:6px">{grades}</div>
        </div>""", unsafe_allow_html=True)
