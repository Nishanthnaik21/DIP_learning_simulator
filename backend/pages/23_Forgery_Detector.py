import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import numpy as np
import cv2
import io
from PIL import Image as PILImage
from utils.theme import inject, page_header, theory_card, metric_row, section_title
from utils.helpers import upload_image, to_gray, normalize_display, comparison_slider, fig_to_st
import matplotlib.pyplot as plt

inject("Forgery Detector", "🕵️")


page_header("Image Forgery Detector — ELA",
            "ERROR LEVEL ANALYSIS · NOISE INCONSISTENCY · COPY-MOVE DETECTION", "🕵️", "#b44fff")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "Error Level Analysis (ELA) exploits JPEG compression artifacts to detect image tampering. "
    "When an image is JPEG compressed, each region reaches a characteristic error level. "
    "If a region has been copy-pasted from another image or edited after compression, its error "
    "level will differ from the surrounding authentic regions. "
    "Tampered regions typically appear brighter (higher error) or show unnatural uniformity. "
    "Based on Module 3 (JPEG restoration/compression theory)."
)

img_rgb = upload_image("ela_up")
gray    = to_gray(img_rgb)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🕵️ ELA Settings")
ela_quality   = st.sidebar.slider("ELA compression quality", 50, 99, 75)
ela_scale     = st.sidebar.slider("ELA amplification", 5, 50, 15)
noise_ksize   = st.sidebar.slider("Noise analysis block size", 4, 32, 8, step=4)
show_advanced = st.sidebar.checkbox("Show advanced analysis", value=True)

# ── ELA computation ───────────────────────────────────────────────────────────
def compute_ela(img_arr, quality=75, scale=15):
    """Compute Error Level Analysis map."""
    pil   = PILImage.fromarray(img_arr)
    buf   = io.BytesIO()
    pil.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    compressed = np.array(PILImage.open(buf))
    if len(compressed.shape) == 2:
        compressed = np.stack([compressed]*3, axis=-1) if len(img_arr.shape)==3 else compressed
    if len(img_arr.shape) == 3 and len(compressed.shape) == 2:
        compressed = np.stack([compressed]*3, axis=-1)
    diff = np.abs(img_arr.astype(float) - compressed.astype(float))
    ela  = np.clip(diff * scale, 0, 255).astype(np.uint8)
    return ela, compressed

def compute_noise_inconsistency(gray_img, block_size=8):
    """Estimate local noise variance — inconsistency may indicate manipulation."""
    h, w    = gray_img.shape
    noise_map = np.zeros((h//block_size, w//block_size))
    for i in range(h//block_size):
        for j in range(w//block_size):
            block = gray_img[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size].astype(float)
            # Estimate noise via high-pass filter residual
            blurred = cv2.GaussianBlur(block, (3,3), 0.5)
            residual = block - blurred
            noise_map[i,j] = np.std(residual)
    return noise_map

def compute_copy_move(gray_img, block_size=16, threshold=0.99):
    """Simple block-based copy-move detection."""
    h, w = gray_img.shape
    blocks, positions = [], []
    step = block_size
    for i in range(0, h-block_size, step):
        for j in range(0, w-block_size, step):
            block = gray_img[i:i+block_size, j:j+block_size].astype(float)
            if block.std() > 5:  # skip uniform blocks
                blocks.append(block.flatten())
                positions.append((i,j))
    if len(blocks) < 2:
        return np.zeros_like(gray_img)
    blocks_arr = np.array(blocks)
    # Normalise each block
    norms = np.linalg.norm(blocks_arr, axis=1, keepdims=True) + 1e-10
    blocks_norm = blocks_arr / norms
    # Dot product similarity
    similarity = blocks_norm @ blocks_norm.T
    np.fill_diagonal(similarity, 0)
    suspicious_map = np.zeros_like(gray_img)
    rows, cols = np.where(similarity > threshold)
    for r, c in zip(rows[:200], cols[:200]):
        if r != c:
            y1, x1 = positions[r]; y2, x2 = positions[c]
            if abs(y1-y2) > block_size or abs(x1-x2) > block_size:  # not adjacent
                suspicious_map[y1:y1+block_size, x1:x1+block_size] = 255
                suspicious_map[y2:y2+block_size, x2:x2+block_size] = 255
    return suspicious_map

# ── Run analysis ───────────────────────────────────────────────────────────────
with st.spinner("Running ELA analysis..."):
    ela_map, compressed = compute_ela(img_rgb, ela_quality, ela_scale)
    ela_gray = ela_map if len(ela_map.shape)==2 else cv2.cvtColor(ela_map, cv2.COLOR_RGB2GRAY)
    ela_colour = cv2.applyColorMap(cv2.normalize(ela_gray, None, 0, 255, cv2.NORM_MINMAX), cv2.COLORMAP_HOT)
    ela_colour = cv2.cvtColor(ela_colour, cv2.COLOR_BGR2RGB)

# ── Top metrics ─────────────────────────────────────────────────────────────
ela_mean   = float(ela_gray.mean())
ela_max    = float(ela_gray.max())
ela_std    = float(ela_gray.std())
ela_high   = float((ela_gray > ela_gray.mean() + 2*ela_gray.std()).mean() * 100)
suspicion  = min(100, ela_mean / 2 + ela_std / 3)

# Verdict
if suspicion > 40:
    verdict, vcolour = "LIKELY TAMPERED", "#ff3366"
elif suspicion > 20:
    verdict, vcolour = "SUSPICIOUS", "#ffb700"
else:
    verdict, vcolour = "LIKELY AUTHENTIC", "#00ff9d"

st.markdown(f"""
<div style="background:rgba(10,30,70,0.55);border:2px solid {vcolour}44;border-radius:14px;
            padding:20px 24px;margin:16px 0;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,transparent,{vcolour},transparent)"></div>
  <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
    <div>
      <div style="font-family:'Orbitron',monospace;font-size:0.68rem;color:#3a6a9a;
                  letter-spacing:0.15em;margin-bottom:4px">FORGERY ANALYSIS VERDICT</div>
      <div style="font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:800;
                  color:{vcolour};text-shadow:0 0 20px {vcolour}66">{verdict}</div>
    </div>
    <div style="flex:1;margin-left:20px">
      <div style="height:8px;background:rgba(0,0,0,0.3);border-radius:4px;margin-bottom:6px;overflow:hidden">
        <div style="width:{min(suspicion,100):.0f}%;height:100%;
                    background:linear-gradient(90deg,#00ff9d,{vcolour});border-radius:4px;
                    box-shadow:0 0 8px {vcolour}88"></div>
      </div>
      <div style="font-size:0.75rem;color:#3a6a9a">
        Suspicion index: <span style="color:{vcolour};font-family:'JetBrains Mono',monospace">{suspicion:.1f}/100</span>
        &nbsp;·&nbsp; ELA mean: {ela_mean:.1f} &nbsp;·&nbsp; ELA std: {ela_std:.1f}
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

metric_row([
    ("ELA Mean",     f"{ela_mean:.1f}"),
    ("ELA Max",      f"{ela_max:.0f}"),
    ("ELA Std",      f"{ela_std:.1f}"),
    ("High ELA %",   f"{ela_high:.1f}%"),
    ("Suspicion",    f"{suspicion:.1f}/100"),
], colors=["#00a8ff","#b44fff","#00fff5","#ffb700","#ff3366"])

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔴 ELA MAP","🔵 NOISE ANALYSIS","🟡 COPY-MOVE","📖 HOW IT WORKS"
])

with tab1:
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown("**Original**"); st.image(img_rgb, use_container_width=True)
    with c2:
        st.markdown("**ELA Map (bright = high error = suspicious)**")
        st.image(ela_colour, use_container_width=True)
    with c3:
        st.markdown("**ELA overlay (50% blend)**")
        if len(img_rgb.shape) == 3:
            blend = cv2.addWeighted(img_rgb, 0.55, ela_colour, 0.45, 0)
        else:
            blend = ela_colour
        st.image(blend, use_container_width=True)
    st.markdown("#### ↔️ Original vs ELA")
    comparison_slider(img_rgb, ela_colour, "Original", "ELA Map", key="ela_cmp")

    # ELA histogram
    fig, ax = plt.subplots(figsize=(8,3), facecolor="#020818")
    ax.set_facecolor("#091428")
    ax.hist(ela_gray.flatten(), bins=64, color="#ff3366", alpha=0.8)
    ax.axvline(ela_mean, color="#00fff5", ls="--", lw=1.5, label=f"Mean={ela_mean:.1f}")
    ax.axvline(ela_mean+2*ela_std, color="#ffb700", ls="--", lw=1, label=f"Mean+2σ={ela_mean+2*ela_std:.1f}")
    ax.set_title("ELA intensity histogram", color="#8ab4d4", fontsize=10)
    ax.legend(fontsize=8); ax.tick_params(colors="#3a6a9a")
    for s in ax.spines.values(): s.set_color("#1a3a5a")
    plt.tight_layout(); fig_to_st(fig)

with tab2:
    if show_advanced:
        with st.spinner("Computing noise inconsistency..."):
            noise_map = compute_noise_inconsistency(gray, noise_ksize)
        noise_disp = cv2.resize(noise_map, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_NEAREST)
        noise_norm = cv2.normalize(noise_disp, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        noise_color= cv2.applyColorMap(noise_norm, cv2.COLORMAP_VIRIDIS)
        noise_color= cv2.cvtColor(noise_color, cv2.COLOR_BGR2RGB)

        c1,c2 = st.columns(2)
        with c1: st.markdown("**Local noise variance map**"); st.image(noise_color, use_container_width=True)
        with c2:
            st.markdown("**Noise inconsistency analysis**")
            fig2, ax2 = plt.subplots(figsize=(6,4), facecolor="#020818")
            ax2.set_facecolor("#091428")
            ax2.imshow(noise_map, cmap="viridis", aspect="auto")
            ax2.set_title("Block noise variance", color="#8ab4d4")
            ax2.axis("off")
            plt.tight_layout(); fig_to_st(fig2)

        theory_card(
            f"Noise variance map ({noise_ksize}×{noise_ksize} blocks): regions with "
            "abnormally low noise (very smooth) may have been generated or heavily processed. "
            "Regions with abnormally high variance may have been sharpened or edited."
        )
    else:
        st.info("Enable 'Show advanced analysis' in the sidebar for noise inconsistency.")

with tab3:
    if show_advanced:
        with st.spinner("Running copy-move detection (may take a moment)..."):
            cm_map = compute_copy_move(gray, block_size=16)
        if cm_map.max() > 0:
            overlay_cm = img_rgb.copy()
            cm_overlay = np.zeros_like(img_rgb)
            cm_overlay[cm_map>0] = [255, 50, 50]
            overlay_cm = cv2.addWeighted(overlay_cm, 0.7, cm_overlay, 0.3, 0)
            n_suspicious = int((cm_map>0).sum() / (16*16))
            c1,c2 = st.columns(2)
            with c1: st.image(img_rgb, caption="Original", use_container_width=True)
            with c2: st.image(overlay_cm, caption=f"Copy-move suspicious regions (red) — {n_suspicious} blocks", use_container_width=True)
        else:
            st.success("✅ No copy-move patterns detected.")
        theory_card(
            "Copy-move detection: image divided into 16×16 blocks. Blocks are compared using "
            "normalised dot product. Pairs with similarity > 0.99 that are non-adjacent are "
            "flagged as potentially copy-moved. This is a simplified version of more advanced "
            "PatchMatch or SIFT-based copy-move detectors."
        )
    else:
        st.info("Enable 'Show advanced analysis' in the sidebar for copy-move detection.")

with tab4:
    st.markdown("""
    <div style="background:rgba(10,30,70,0.45);border:1px solid rgba(180,79,255,0.2);
                border-radius:12px;padding:20px 24px">
      <div style="font-family:'Orbitron',monospace;font-size:0.75rem;color:#b44fff;
                  letter-spacing:0.1em;margin-bottom:14px">HOW ELA WORKS</div>
      <ol style="font-size:0.84rem;color:#8ab4d4;line-height:2;margin:0;padding-left:20px">
        <li>Take the original image (possibly already JPEG-compressed once)</li>
        <li>Re-compress it to JPEG at a known quality (e.g. 75)</li>
        <li>Compute pixel-wise absolute difference: ELA = |original − recompressed| × scale</li>
        <li>Authentic regions show uniform, low ELA values (they've been compressed before)</li>
        <li>Edited/pasted regions show higher ELA values — they contain more error after re-compression</li>
        <li>Uniform colour fills show very dark ELA (near zero) — suspicious in photographic scenes</li>
      </ol>
      <br>
      <div style="font-size:0.78rem;color:#3a6a9a;border-top:1px solid rgba(180,79,255,0.15);
                  padding-top:12px;margin-top:8px">
        ⚠️ <b>Limitations:</b> ELA is a heuristic, not proof. Multiple JPEG saves can make authentic images
        appear suspicious. Raw/PNG images will show high ELA everywhere. Always use alongside other evidence.
        This tool is for educational demonstration of JPEG compression theory (Module 3).
      </div>
    </div>""", unsafe_allow_html=True)
