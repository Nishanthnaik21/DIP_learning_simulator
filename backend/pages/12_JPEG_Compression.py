import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import io
from utils.theme import inject, page_header, theory_card, metric_row, code_card
from utils.helpers import upload_image, to_gray, normalize_display, psnr, fig_to_st, comparison_slider

inject("JPEG Compression", "🗜️")


page_header("JPEG / DCT Compression Simulator",
            "VISUALISE 8×8 DCT BLOCKS, QUANTIZATION, AND QUALITY vs PSNR TRADEOFF", "🗜️", "#a855f7")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


img_rgb  = upload_image("jpeg_up")
gray     = to_gray(img_rgb)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### 🗜️ Compression Settings")
quality   = st.sidebar.slider("JPEG Quality (1–100)", 1, 100, 50)
show_blocks = st.sidebar.checkbox("Show 8×8 block grid overlay", value=True)
block_region = st.sidebar.checkbox("Zoom into one 8×8 block", value=True)

theory_card(
    "JPEG compression uses the Discrete Cosine Transform (DCT). The image is divided into 8×8 pixel blocks. "
    "Each block is transformed to frequency domain using DCT-II. High-frequency coefficients (fine detail) "
    "are divided by a quantization matrix — higher quality means smaller divisors, preserving more detail. "
    "The quantized coefficients are then entropy-coded (Huffman). On decompression, inverse DCT reconstructs the pixels. "
    "At low quality, blocking artefacts appear because each 8×8 block is reconstructed independently.",
    "How JPEG Works"
)

# ── JPEG compress/decompress via PIL ─────────────────────────────────────────
def jpeg_compress(img_gray: np.ndarray, q: int) -> np.ndarray:
    pil = __import__("PIL").Image.fromarray(img_gray.astype(np.uint8))
    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=q)
    buf.seek(0)
    return np.array(__import__("PIL").Image.open(buf).convert("L"))

# ── DCT on one 8x8 block ──────────────────────────────────────────────────────
def dct_block(block):
    """Return DCT-II coefficients of 8×8 block."""
    b = block.astype(np.float32) - 128.0
    return cv2.dct(b)

def idct_block(coeffs):
    return np.clip(cv2.idct(coeffs) + 128.0, 0, 255).astype(np.uint8)

# Standard JPEG luminance quantization table (quality ~50)
QUANT_TABLE_50 = np.array([
    [16,11,10,16,24,40,51,61],
    [12,12,14,19,26,58,60,55],
    [14,13,16,24,40,57,69,56],
    [14,17,22,29,51,87,80,62],
    [18,22,37,56,68,109,103,77],
    [24,35,55,64,81,104,113,92],
    [49,64,78,87,103,121,120,101],
    [72,92,95,98,112,100,103,99],
], dtype=np.float32)

def get_quant_table(quality: int) -> np.ndarray:
    if quality < 50:
        scale = 5000 / quality
    else:
        scale = 200 - 2 * quality
    qt = np.clip(np.floor((QUANT_TABLE_50 * scale + 50) / 100), 1, 255).astype(np.float32)
    return qt

# ── Run compression ───────────────────────────────────────────────────────────
compressed = jpeg_compress(gray, quality)

# Estimate file size
buf_orig = io.BytesIO()
__import__("PIL").Image.fromarray(gray).save(buf_orig, format="PNG")
orig_size = len(buf_orig.getvalue())

buf_comp = io.BytesIO()
__import__("PIL").Image.fromarray(gray).save(buf_comp, format="JPEG", quality=quality)
comp_size = len(buf_comp.getvalue())
ratio     = orig_size / max(comp_size, 1)
psnr_val  = psnr(gray, compressed)

# ── Top metrics ────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Quality",          f"{quality}/100")
c2.metric("PSNR",             f"{psnr_val:.1f} dB")
c3.metric("Original size",    f"{orig_size//1024} KB")
c4.metric("Compressed size",  f"{comp_size//1024} KB")
c5.metric("Compression ratio",f"{ratio:.1f}×")

st.markdown("<br>", unsafe_allow_html=True)

# ── Block grid overlay ─────────────────────────────────────────────────────────
def draw_block_grid(img, step=8):
    overlay = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB) if len(img.shape)==2 else img.copy()
    h, w = img.shape[:2]
    for y in range(0, h, step):
        cv2.line(overlay, (0,y), (w,y), (0,200,120), 1)
    for x in range(0, w, step):
        cv2.line(overlay, (x,0), (x,h), (0,200,120), 1)
    return overlay

tab1, tab2, tab3, tab4 = st.tabs([
    "🖼️ COMPRESSION OUTPUT", "🔬 8×8 DCT BLOCK", "📈 QUALITY CURVE", "💻 DCT CODE"
])

with tab1:
    col1, col2 = st.columns(2)
    disp_orig = draw_block_grid(gray) if show_blocks else cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    disp_comp = draw_block_grid(compressed) if show_blocks else cv2.cvtColor(compressed, cv2.COLOR_GRAY2RGB)
    with col1:
        st.markdown("**Original (PNG lossless)**")
        st.image(disp_orig, use_container_width=True)
    with col2:
        st.markdown(f"**JPEG quality={quality} — ratio {ratio:.1f}×**")
        st.image(disp_comp, use_container_width=True)

    st.markdown("#### ↔️ Drag to compare")
    comparison_slider(gray, compressed, "Original", f"JPEG Q={quality}", key=f"jpeg_q{quality}")

    # Download compressed
    buf_dl = io.BytesIO()
    __import__("PIL").Image.fromarray(gray).save(buf_dl, format="JPEG", quality=quality)
    buf_dl.seek(0)
    st.download_button(f"⬇ Download JPEG (Q={quality})", buf_dl,
                       f"compressed_q{quality}.jpg", "image/jpeg")

with tab2:
    bx = st.slider("Block column (x)", 0, gray.shape[1]//8-1, gray.shape[1]//16)
    by = st.slider("Block row (y)",    0, gray.shape[0]//8-1, gray.shape[0]//16)

    x1,y1 = bx*8, by*8
    block_orig = gray[y1:y1+8, x1:x1+8].astype(np.float32)
    block_comp = compressed[y1:y1+8, x1:x1+8].astype(np.float32)
    dct_coeffs = dct_block(block_orig)
    qt         = get_quant_table(quality)
    dct_quant  = np.round(dct_coeffs / qt)

    fig, axes = plt.subplots(2, 3, figsize=(14, 7), facecolor="#0b0f1a")
    for ax in axes.flat:
        ax.set_facecolor("#1a2235")

    axes[0,0].imshow(block_orig, cmap="gray", vmin=0, vmax=255)
    axes[0,0].set_title("Original 8×8 block", color="#e2e8f0"); axes[0,0].axis("off")

    axes[0,1].imshow(np.abs(dct_coeffs), cmap="inferno")
    axes[0,1].set_title("DCT coefficients (|F|)", color="#e2e8f0"); axes[0,1].axis("off")

    axes[0,2].imshow(np.abs(dct_quant), cmap="plasma")
    axes[0,2].set_title(f"Quantized (Q={quality})", color="#e2e8f0"); axes[0,2].axis("off")

    axes[1,0].imshow(block_comp, cmap="gray", vmin=0, vmax=255)
    axes[1,0].set_title("Reconstructed block", color="#e2e8f0"); axes[1,0].axis("off")

    axes[1,1].imshow(qt, cmap="viridis")
    axes[1,1].set_title("Quantization table", color="#e2e8f0"); axes[1,1].axis("off")

    diff = np.abs(block_orig - block_comp)
    axes[1,2].imshow(diff, cmap="hot")
    axes[1,2].set_title("Block error (|orig−recon|)", color="#e2e8f0"); axes[1,2].axis("off")

    plt.tight_layout(); fig_to_st(fig)

    # Coefficient heatmap table
    st.markdown("**DCT coefficient matrix (top-left = DC, rest = AC):**")
    coeff_display = np.abs(dct_coeffs).astype(int)
    col_labels = [f"F{i}" for i in range(8)]
    import pandas as pd
    df = pd.DataFrame(coeff_display, columns=col_labels)
    st.dataframe(df, use_container_width=True)

    non_zero = (dct_quant != 0).sum()
    theory_card(f"DC coefficient (top-left) = average block intensity = {dct_coeffs[0,0]:.1f}. "
                f"After quantization at Q={quality}, {non_zero}/64 coefficients are non-zero "
                f"({non_zero/64*100:.0f}% retained). Lower quality → fewer non-zero coefficients → smaller file.")

with tab3:
    st.markdown("#### PSNR & File Size vs Quality Curve")
    qualities = [1,5,10,15,20,30,40,50,60,70,80,90,95,100]
    psnr_vals, size_vals = [], []
    for q in qualities:
        comp_q = jpeg_compress(gray, q)
        psnr_vals.append(psnr(gray, comp_q))
        buf_q = io.BytesIO()
        __import__("PIL").Image.fromarray(gray).save(buf_q, format="JPEG", quality=q)
        size_vals.append(len(buf_q.getvalue()) / 1024)

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor="#0b0f1a")
    for ax in [ax1, ax2]: ax.set_facecolor("#1a2235")

    ax1.plot(qualities, psnr_vals, color="#4f8ef7", linewidth=2.5, marker="o", markersize=4)
    ax1.axvline(quality, color="#fbbf24", linestyle="--", alpha=0.7, label=f"Q={quality}")
    ax1.axhline(psnr_val, color="#22d3a5", linestyle=":", alpha=0.7)
    ax1.set_title("PSNR vs Quality", color="#e2e8f0"); ax1.set_xlabel("Quality", color="#94a3b8")
    ax1.set_ylabel("PSNR (dB)", color="#94a3b8"); ax1.tick_params(colors="#64748b")
    ax1.legend(fontsize=9); [s.set_color("#2a3a55") for s in ax1.spines.values()]

    ax2.plot(qualities, size_vals, color="#a855f7", linewidth=2.5, marker="s", markersize=4)
    ax2.axvline(quality, color="#fbbf24", linestyle="--", alpha=0.7, label=f"Q={quality}")
    ax2.set_title("File Size vs Quality", color="#e2e8f0"); ax2.set_xlabel("Quality", color="#94a3b8")
    ax2.set_ylabel("Size (KB)", color="#94a3b8"); ax2.tick_params(colors="#64748b")
    ax2.legend(fontsize=9); [s.set_color("#2a3a55") for s in ax2.spines.values()]

    plt.tight_layout(); fig_to_st(fig2)
    st.markdown(f"**At Q={quality}:** PSNR = {psnr_val:.1f} dB, Size = {comp_size//1024} KB, Ratio = {ratio:.1f}×")

with tab4:
    code_card(f'''import cv2
import numpy as np
from PIL import Image
import io

# ── JPEG-style DCT compression ─────────────────────────────────────────────
QUALITY = {quality}

def jpeg_compress_gray(gray_img: np.ndarray, quality: int) -> np.ndarray:
    """Compress grayscale image using PIL JPEG and return numpy array."""
    pil   = Image.fromarray(gray_img.astype(np.uint8))
    buf   = io.BytesIO()
    pil.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return np.array(Image.open(buf).convert("L"))

def dct_8x8_block(block: np.ndarray) -> np.ndarray:
    """Apply DCT-II to a single 8×8 block."""
    return cv2.dct(block.astype(np.float32) - 128.0)

def idct_8x8_block(coeffs: np.ndarray) -> np.ndarray:
    """Apply inverse DCT to recover pixel values."""
    return np.clip(cv2.idct(coeffs) + 128.0, 0, 255).astype(np.uint8)

# Load and compress
img   = cv2.imread("image.jpg", cv2.IMREAD_GRAYSCALE)
comp  = jpeg_compress_gray(img, QUALITY)

# Compute PSNR
mse   = np.mean((img.astype(float) - comp.astype(float)) ** 2)
psnr  = 20 * np.log10(255.0 / np.sqrt(mse))
print(f"PSNR: {{psnr:.1f}} dB")

# Inspect one 8×8 block
block   = img[0:8, 0:8]
dct_c   = dct_8x8_block(block)
print("DC coefficient:", dct_c[0, 0])   # = mean intensity of block
print("Non-zero AC coefficients:", (dct_c != 0).sum() - 1)
''')
