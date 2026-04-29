import cv2
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
import io, os, base64, textwrap, functools
from datetime import datetime

# ── Common header ──────────────────────────────────────────────────────────────
def page_header(module_num, title, icon, desc):
    st.set_page_config(page_title=f"Module {module_num} – {title}", page_icon=icon, layout="wide")
    st.markdown(f"## {icon} Module {module_num}: {title}")
    st.caption(desc)
    st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE 1 — SAMPLE IMAGE GALLERY
# ═══════════════════════════════════════════════════════════════════════════════
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "samples")

SAMPLE_META = {
    "cameraman.png":     {"name": "Cameraman",        "best_for": "M2 Edges, M5 Segmentation",   "desc": "Classic benchmark — great for edge & restoration demos"},
    "lena.png":          {"name": "Lena (synthetic)",  "best_for": "M2 Filters, M4 Color",        "desc": "Standard test portrait — rich colour & texture"},
    "coins.png":         {"name": "Coins",             "best_for": "M4 Morphology, M5 Hough",     "desc": "Circular objects — ideal for morphological ops & Hough circles"},
    "circuit.png":       {"name": "Circuit Board",     "best_for": "M2 Sharpening, M5 Edges",    "desc": "Fine lines & corners — great for edge & frequency domain"},
    "baboon.png":        {"name": "Baboon",            "best_for": "M4 Color, M2 Histogram",      "desc": "High-saturation colour image — perfect for colour space demos"},
    "checkerboard.png":  {"name": "Checkerboard",      "best_for": "M1 Sampling, M2 DFT",         "desc": "Regular pattern — shows aliasing & DFT peaks clearly"},
    "gradient_ramp.png": {"name": "Gradient Ramp",     "best_for": "M1 Quantization, M2 Hist",   "desc": "Linear gradient — ideal for quantization & histogram demos"},
    "text_doc.png":      {"name": "Text Document",     "best_for": "M5 Thresholding, M2 CLAHE",  "desc": "Uneven illumination text — adaptive threshold demo"},
    "xray.png":          {"name": "X-Ray (synthetic)", "best_for": "M3 Restoration, M2 CLAHE",   "desc": "Medical-style image — noise & restoration demos"},
    "satellite.png":     {"name": "Satellite View",    "best_for": "M4 Pseudo-color, M5 Seg",    "desc": "Aerial scene — colour & segmentation demos"},
}

def sample_gallery(key="sample_pick"):
    """Show sample image picker. Returns selected image as RGB array or None."""
    st.markdown("##### 🖼️ Sample Gallery")
    sample_names = {v["name"]: k for k, v in SAMPLE_META.items()}
    choice = st.selectbox(
        "Choose a classic test image",
        ["— Upload your own —"] + list(sample_names.keys()),
        key=f"gallery_{key}"
    )
    if choice == "— Upload your own —":
        return None
    fname = sample_names[choice]
    path  = os.path.join(SAMPLES_DIR, fname)
    if not os.path.exists(path):
        st.warning("Sample not found. Run: python3 assets/generate_samples.py")
        return None
    meta = SAMPLE_META[fname]
    st.caption(f"✅ Best for: {meta['best_for']} — {meta['desc']}")
    img = cv2.imread(path)
    if img is None:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img

def upload_image(key="img_upload"):
    """Upload or select from gallery. Upload takes priority over gallery."""
    c1, c2 = st.columns(2)
    with c1:
        gallery_img = sample_gallery(key)
    with c2:
        st.markdown("##### 📁 Upload Your Image")
        uploaded = st.file_uploader("Upload image (JPG/PNG)", type=["jpg","jpeg","png"], key=key, label_visibility="collapsed")
    
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        return np.array(img)
    if gallery_img is not None:
        return gallery_img
    return make_test_image()

# ── Built-in synthetic test image (cached — always identical) ──────────────
@st.cache_data(show_spinner=False)
def make_test_image():
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    for i in range(256): img[i, :, 0] = i
    for i in range(256): img[:, i, 1] = i
    img[:, :, 2] = 128
    cv2.rectangle(img, (30, 30), (100, 100), (255, 255, 255), -1)
    cv2.circle(img, (180, 80), 50, (30, 30, 180), -1)
    cv2.putText(img, "DIP", (80, 170), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,0), 3)
    rng = np.random.default_rng(42)  # fixed seed for reproducibility
    noise = rng.integers(0, 30, img.shape, dtype=np.uint8)
    return cv2.add(img, noise)

# ── Standard display helpers ───────────────────────────────────────────────────
def show_images(imgs_labels, n_cols=2, cmap=None):
    cols = st.columns(n_cols)
    for idx, (img, label) in enumerate(imgs_labels):
        with cols[idx % n_cols]:
            st.markdown(f"**{label}**")
            st.image(img, use_container_width=True, clamp=True)

def to_gray(img):
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img

def fig_to_st(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)

def theory_box(text):
    st.markdown(f"""
    <div style="background:#f0f4ff;border-left:4px solid #4f6ef7;border-radius:0 8px 8px 0;
    padding:12px 16px;margin:10px 0;font-size:0.88rem;color:#2d3a6b;line-height:1.6">
    📖 <b>Theory:</b> {text}
    </div>""", unsafe_allow_html=True)

def metric_row(items):
    cols = st.columns(len(items))
    for col, (label, val) in zip(cols, items):
        col.metric(label, val)

def psnr(original, noisy):
    mse = np.mean((original.astype(float) - noisy.astype(float))**2)
    if mse == 0: return 100.0
    return 20 * np.log10(255.0 / np.sqrt(mse))

def normalize_display(img):
    img = np.array(img, dtype=float)
    mn, mx = img.min(), img.max()
    if mx == mn: return np.zeros_like(img, dtype=np.uint8)
    return ((img - mn) / (mx - mn) * 255).astype(np.uint8)

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE 2 — BEFORE/AFTER COMPARISON SLIDER
# ═══════════════════════════════════════════════════════════════════════════════
def comparison_slider(before: np.ndarray, after: np.ndarray,
                       label_before="Original", label_after="Processed",
                       key="compare"):
    """Interactive drag-to-compare image slider using inline HTML/JS."""
    def img_to_b64(arr):
        if arr is None: return ""
        if len(arr.shape) == 2:
            arr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_GRAY2RGB)
        arr_u8 = np.clip(arr, 0, 255).astype(np.uint8)
        pil = Image.fromarray(arr_u8)
        pil = pil.resize((512, 512), Image.LANCZOS)
        buf = io.BytesIO(); pil.save(buf, format="PNG"); buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    b64_before = img_to_b64(before)
    b64_after  = img_to_b64(after)
    uid = key.replace(" ","_").replace("-","_")

    html = f"""
<div style="max-width:540px;margin:0 auto;font-family:sans-serif">
  <div style="position:relative;overflow:hidden;border-radius:10px;
              border:1.5px solid #c5cae9;cursor:ew-resize;height:320px"
       id="wrap_{uid}">
    <!-- After image -->
    <img src="data:image/png;base64,{b64_after}"
         style="width:100%;height:320px;object-fit:cover;display:block;user-select:none"/>
    <!-- Before image clipped -->
    <div id="clip_{uid}" style="position:absolute;top:0;left:0;width:50%;
                                 overflow:hidden;height:100%;pointer-events:none">
      <img src="data:image/png;base64,{b64_before}"
           style="width:540px;max-width:none;height:320px;object-fit:cover;
                  display:block;user-select:none"/>
    </div>
    <!-- Divider -->
    <div id="line_{uid}" style="position:absolute;top:0;left:50%;width:3px;
         height:100%;background:white;box-shadow:0 0 8px rgba(0,0,0,0.4);z-index:10">
      <div style="position:absolute;top:50%;left:50%;
           transform:translate(-50%,-50%);background:white;border-radius:50%;
           width:36px;height:36px;display:flex;align-items:center;justify-content:center;
           box-shadow:0 2px 10px rgba(0,0,0,0.3);font-size:16px;pointer-events:none">⇔</div>
    </div>
    <!-- Labels -->
    <div style="position:absolute;top:8px;left:8px;background:rgba(0,0,0,0.6);
         color:white;padding:4px 10px;border-radius:4px;font-size:12px;font-weight:600;
         pointer-events:none">{label_before}</div>
    <div style="position:absolute;top:8px;right:8px;background:rgba(79,110,247,0.85);
         color:white;padding:4px 10px;border-radius:4px;font-size:12px;font-weight:600;
         pointer-events:none">{label_after}</div>
  </div>
  <input type="range" min="0" max="100" value="50" id="sl_{uid}"
         style="width:100%;margin-top:8px;accent-color:#4f6ef7"
         oninput="move_{uid}(this.value)"/>
  <div style="display:flex;justify-content:space-between;font-size:11px;color:#888">
    <span>← {label_before}</span><span>{label_after} →</span>
  </div>
</div>
<script>
function move_{uid}(val) {{
  var pct = val + "%";
  document.getElementById("clip_{uid}").style.width = pct;
  document.getElementById("line_{uid}").style.left  = pct;
}}
// Drag on image
(function() {{
  var wrap = document.getElementById("wrap_{uid}");
  var dragging = false;
  wrap.addEventListener("mousedown",  function(e){{ dragging=true; }});
  document.addEventListener("mouseup",function(e){{ dragging=false; }});
  wrap.addEventListener("mousemove",  function(e){{
    if(!dragging) return;
    var rect = wrap.getBoundingClientRect();
    var pct  = Math.max(0,Math.min(100,(e.clientX-rect.left)/rect.width*100));
    document.getElementById("sl_{uid}").value = pct;
    move_{uid}(pct);
  }});
  wrap.addEventListener("touchmove",  function(e){{
    var rect = wrap.getBoundingClientRect();
    var pct  = Math.max(0,Math.min(100,(e.touches[0].clientX-rect.left)/rect.width*100));
    document.getElementById("sl_{uid}").value = pct;
    move_{uid}(pct);
  }}, {{passive:true}});
}})();
</script>
"""
    st.components.v1.html(html, height=400, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE 3 — SUPER RESOLUTION (no ML needed — high-quality interpolation)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False, max_entries=32)
def super_resolve(img: np.ndarray, scale: int = 2, mode: str = "Lanczos + Sharpen") -> np.ndarray:
    """Upscale using high-quality interpolation + optional post-sharpening.
    Cached so the same (img, scale, mode) combination is only computed once.
    Modes: Nearest | Bilinear | Bicubic | Lanczos | Lanczos + Sharpen | Lanczos + Edge-Boost
    """
    h, w = img.shape[:2]
    interp_map = {
        "Nearest":              cv2.INTER_NEAREST,
        "Bilinear":             cv2.INTER_LINEAR,
        "Bicubic":              cv2.INTER_CUBIC,
        "Lanczos":              cv2.INTER_LANCZOS4,
        "Lanczos + Sharpen":    cv2.INTER_LANCZOS4,
        "Lanczos + Edge-Boost": cv2.INTER_LANCZOS4,
    }
    interp   = interp_map.get(mode, cv2.INTER_LANCZOS4)
    upscaled = cv2.resize(img, (w * scale, h * scale), interpolation=interp)

    if mode == "Lanczos + Sharpen":
        blur     = cv2.GaussianBlur(upscaled, (0,0), 1.5)
        upscaled = np.clip(cv2.addWeighted(upscaled, 1.6, blur, -0.6, 0), 0, 255).astype(np.uint8)

    elif mode == "Lanczos + Edge-Boost":
        g = upscaled if len(upscaled.shape)==2 else cv2.cvtColor(upscaled, cv2.COLOR_RGB2GRAY)
        lap = cv2.Laplacian(g.astype(np.float32), cv2.CV_32F)
        if len(upscaled.shape) == 3:
            lap3 = np.stack([lap]*3, axis=-1)
            upscaled = np.clip(upscaled.astype(float) - 0.35*lap3, 0, 255).astype(np.uint8)
        else:
            upscaled = np.clip(upscaled.astype(float) - 0.35*lap, 0, 255).astype(np.uint8)

    return upscaled

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE 4 — PDF LAB REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════
def generate_pdf_report(operations: list, student_name: str = "",
                         roll_no: str = "", module_name: str = "") -> bytes:
    """
    Generate a complete PDF lab record.
    operations: list of dicts with keys:
        title (str), theory (str), parameters (dict),
        before_img (np.ndarray), after_img (np.ndarray), metrics (dict)
    Returns: PDF as bytes.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                         TableStyle, Image as RLImage, HRFlowable, PageBreak)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        return b""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.8*cm, rightMargin=1.8*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    H1   = ParagraphStyle("H1",   parent=styles["Heading1"], fontSize=16,
                           textColor=colors.HexColor("#1a237e"), alignment=TA_CENTER, spaceAfter=4)
    H2   = ParagraphStyle("H2",   parent=styles["Heading2"], fontSize=12,
                           textColor=colors.HexColor("#283593"), spaceBefore=12, spaceAfter=4)
    BODY = ParagraphStyle("Body", parent=styles["Normal"],   fontSize=9.5, leading=14, spaceAfter=4)
    SMALL= ParagraphStyle("Small",parent=styles["Normal"],   fontSize=8,   textColor=colors.grey, leading=11)
    CAP  = ParagraphStyle("Cap",  parent=styles["Normal"],   fontSize=8,   alignment=TA_CENTER,
                           textColor=colors.HexColor("#555555"))

    def np_to_rl(arr, w_cm=6.5):
        if arr is None: return None
        if len(arr.shape) == 2: arr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_GRAY2RGB)
        arr = cv2.resize(arr, (300,300))
        pil = Image.fromarray(np.clip(arr,0,255).astype(np.uint8))
        b = io.BytesIO(); pil.save(b,"PNG"); b.seek(0)
        return RLImage(b, width=w_cm*cm, height=w_cm*cm)

    story = []

    # Header
    story.append(Paragraph("DIP Learning Simulator — Lab Record", H1))
    story.append(Paragraph("Digital Image Processing Simulator", SMALL))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#3949ab"), spaceAfter=10))

    info = Table([
        ["Student Name", student_name or "—", "Roll No.", roll_no or "—"],
        ["Module",       module_name  or "—", "Date",     datetime.now().strftime("%d %b %Y")],
    ], colWidths=[3.2*cm, 6.3*cm, 3.2*cm, 4.3*cm])
    info.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,-1), colors.HexColor("#e8eaf6")),
        ("BACKGROUND", (2,0),(2,-1), colors.HexColor("#e8eaf6")),
        ("FONTNAME",   (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#c5cae9")),
        ("PADDING",    (0,0),(-1,-1), 5),
    ]))
    story.append(info)
    story.append(Spacer(1, 0.5*cm))

    for idx, op in enumerate(operations, 1):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#c5cae9"), spaceBefore=8))
        story.append(Paragraph(f"Experiment {idx}: {op.get('title','Operation')}", H2))

        story.append(Paragraph("<b>Aim:</b>", BODY))
        story.append(Paragraph(
            f"To apply {op.get('title','')} on a digital image using Python and OpenCV "
            "and observe the effect on image quality.", BODY))

        if op.get("theory"):
            story.append(Paragraph("<b>Theory:</b>", BODY))
            for line in textwrap.wrap(op["theory"], 105):
                story.append(Paragraph(line, BODY))

        if op.get("parameters"):
            story.append(Paragraph("<b>Parameters:</b>", BODY))
            pr = Table([["Parameter","Value"]] + [[str(k),str(v)] for k,v in op["parameters"].items()],
                       colWidths=[6*cm, 11*cm])
            pr.setStyle(TableStyle([
                ("BACKGROUND",  (0,0),(-1,0), colors.HexColor("#3949ab")),
                ("TEXTCOLOR",   (0,0),(-1,0), colors.white),
                ("FONTNAME",    (0,0),(-1,-1), "Helvetica"),
                ("FONTSIZE",    (0,0),(-1,-1), 8.5),
                ("GRID",        (0,0),(-1,-1), 0.5, colors.HexColor("#c5cae9")),
                ("PADDING",     (0,0),(-1,-1), 4),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f5f5ff")]),
            ]))
            story.append(pr); story.append(Spacer(1,0.2*cm))

        bi = np_to_rl(op.get("before_img"))
        ai = np_to_rl(op.get("after_img"))
        if bi and ai:
            story.append(Paragraph("<b>Input vs Output:</b>", BODY))
            it = Table([[bi, ai],[Paragraph("Original Image",CAP),Paragraph("Processed Image",CAP)]],
                       colWidths=[8*cm, 8*cm])
            it.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                                     ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                                     ("PADDING",(0,0),(-1,-1),4)]))
            story.append(it); story.append(Spacer(1,0.2*cm))

        if op.get("metrics"):
            story.append(Paragraph("<b>Results & Observations:</b>", BODY))
            mr = Table([["Metric","Value"]] + [[str(k),str(v)] for k,v in op["metrics"].items()],
                       colWidths=[8*cm, 9*cm])
            mr.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#e8eaf6")),
                ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
                ("FONTSIZE",(0,0),(-1,-1),8.5),
                ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#c5cae9")),
                ("PADDING",(0,0),(-1,-1),4),
            ]))
            story.append(mr)

        story.append(Paragraph("<b>Conclusion:</b>", BODY))
        story.append(Paragraph(
            f"The {op.get('title','operation')} was successfully implemented. "
            "The result confirms the theoretical behaviour described in the course syllabus.", BODY))
        story.append(Spacer(1,0.3*cm))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#3949ab")))
    story.append(Paragraph("DIP Learning Simulator · 22AIM61 · Generated automatically", SMALL))
    doc.build(story)
    buf.seek(0)
    return buf.read()

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE 5 — QUIZ BANK + RENDERER
# ═══════════════════════════════════════════════════════════════════════════════
QUIZ_BANK = {
    "Module 1 — Fundamentals": [
        {"q": "What does increasing the sampling rate of a digital image do?",
         "opts": ["Increases number of grey levels","Increases spatial resolution","Increases brightness","Reduces image size"],
         "ans": 1, "exp": "Sampling rate = how many pixels represent the scene. Higher sampling → more spatial detail."},
        {"q": "How many grey levels does a 3-bit image have?",
         "opts": ["3","6","8","16"],
         "ans": 2, "exp": "2^N gives the number of grey levels. 2^3 = 8."},
        {"q": "In 4-connectivity, how many neighbours does a pixel have?",
         "opts": ["2","4","6","8"],
         "ans": 1, "exp": "4-connectivity: Up, Down, Left, Right only — the 4 edge-adjacent pixels."},
        {"q": "Gamma correction I_out = I_in^γ. When γ = 0.5, the image is:",
         "opts": ["Darkened","Unchanged","Brightened","Inverted"],
         "ans": 2, "exp": "γ < 1 maps dark pixels to brighter values → overall brightening effect."},
        {"q": "What operation produces I_out = 255 − I_in?",
         "opts": ["Thresholding","Image negative","Gamma correction","Log transform"],
         "ans": 1, "exp": "The image negative formula — bright becomes dark, dark becomes bright."},
    ],
    "Module 2 — Spatial & Frequency": [
        {"q": "Which filter best removes salt-and-pepper noise while preserving edges?",
         "opts": ["Average filter","Gaussian filter","Median filter","Bilateral filter"],
         "ans": 2, "exp": "Median filter replaces each pixel with the neighbourhood median — eliminates impulse noise without blurring edges."},
        {"q": "Histogram equalisation works by:",
         "opts": ["Stretching image spatially","Making the histogram approximately uniform","Reducing noise","Sharpening edges"],
         "ans": 1, "exp": "HE maps intensities so the CDF becomes linear — flattening the histogram and improving contrast."},
        {"q": "After fftshift, the DFT centre represents:",
         "opts": ["High-frequency edges","DC component (zero frequency)","Random noise","Phase only"],
         "ans": 1, "exp": "fftshift moves DC (= average brightness = zero frequency) to the image centre for easy visualisation."},
        {"q": "An ideal low-pass filter causes which artefact?",
         "opts": ["Blocking artefact","Ringing (Gibbs effect)","Salt-and-pepper","Posterization"],
         "ans": 1, "exp": "The sharp spectral cutoff corresponds to a sinc function in space — causing ringing oscillations near edges."},
        {"q": "The unsharp masking formula is:",
         "opts": ["f_out = f − blur","f_out = f + α(f − blur)","f_out = blur + αf","f_out = f × blur"],
         "ans": 1, "exp": "Add scaled high-frequency 'mask' (original − blur) back to original. α controls sharpening strength."},
    ],
    "Module 3 — Restoration": [
        {"q": "In Wiener filtering, K represents:",
         "opts": ["Kernel size","Noise-to-signal power ratio","Blur angle","Filter order"],
         "ans": 1, "exp": "K = Sη/Sf. K=0 → pure inverse filter. Large K → strong regularisation against noise."},
        {"q": "Inverse filtering fails mainly because:",
         "opts": ["It needs a GPU","Dividing by small H values amplifies noise catastrophically","It only works on colour images","It cannot handle motion blur"],
         "ans": 1, "exp": "F̂ = G/H. Where H is near zero, even tiny noise η is amplified enormously."},
        {"q": "Gaussian noise follows which probability distribution?",
         "opts": ["Uniform","Rayleigh","Normal (bell curve)","Exponential"],
         "ans": 2, "exp": "Gaussian noise ~ N(μ, σ²) — the most common electronic sensor noise model."},
        {"q": "Constrained Least Squares filtering minimises:",
         "opts": ["Image file size","Laplacian energy subject to a data fitting constraint","Number of pixels","Histogram entropy"],
         "ans": 1, "exp": "CLS minimises ||Pf̂||² (Laplacian smoothness) subject to ||g − Hf̂|| = ||η||."},
        {"q": "PSNR = 100 dB means:",
         "opts": ["Very poor quality","Average quality","Perfect reconstruction (MSE = 0)","Heavy noise"],
         "ans": 2, "exp": "PSNR = 20×log10(255/√MSE). MSE=0 → PSNR→∞ (shown as 100 in practice)."},
    ],
    "Module 4 — Color & Morphology": [
        {"q": "HSV separates which properties?",
         "opts": ["Red Green Blue","Hue Saturation Value","Height Sharpness Volume","Highlight Shadow Vibrance"],
         "ans": 1, "exp": "HSV = Hue (colour type 0–360°), Saturation (purity), Value (brightness). Great for colour segmentation."},
        {"q": "Morphological erosion:",
         "opts": ["Expands bright regions","Shrinks bright regions","Fills holes","Detects edges"],
         "ans": 1, "exp": "A pixel is foreground only if ALL SE pixels are also foreground → objects shrink, small ones disappear."},
        {"q": "Opening = Erosion then Dilation. Its purpose is:",
         "opts": ["Fill dark holes","Remove small bright noise","Detect corners","Sharpen edges"],
         "ans": 1, "exp": "Opening removes foreground regions smaller than the SE without affecting larger objects."},
        {"q": "The wavelet approximation sub-band contains:",
         "opts": ["High-frequency edge detail","Low-frequency overall structure","Random noise","Phase information"],
         "ans": 1, "exp": "LL sub-band = low-pass filtered downsampled version — represents the overall image structure at that scale."},
        {"q": "Pseudo-colour adds real colour information to a grayscale image. True or False?",
         "opts": ["True","False","Only for medical images","Only for satellite images"],
         "ans": 1, "exp": "FALSE. Pseudo-colour maps intensity → colour via LUT. It enhances visual discrimination but adds NO new colour information."},
    ],
    "Module 5 — Segmentation": [
        {"q": "Canny's step that thins edges to single-pixel width is:",
         "opts": ["Gaussian smoothing","Non-maximum suppression","Double thresholding","Hysteresis"],
         "ans": 1, "exp": "NMS checks if each pixel is a local maximum along the gradient direction. If not → suppressed to 0."},
        {"q": "Otsu's threshold is found by:",
         "opts": ["Using 127 always","Minimising intra-class variance","Using histogram mean","Using Fourier analysis"],
         "ans": 1, "exp": "Otsu tests all possible thresholds and picks the one minimising σ²_w = w₁σ₁² + w₂σ₂²."},
        {"q": "Hough line transform maps image space (x,y) to:",
         "opts": ["Scale space","(ρ, θ) parameter space","(u,v) frequency space","Wavelet space"],
         "ans": 1, "exp": "Each edge pixel votes for all (ρ,θ) lines through it. Peaks in accumulator = actual lines in the image."},
        {"q": "Harris R = det(M) − k·trace(M)². A pixel is a corner when:",
         "opts": ["R is large and negative","R is close to zero","R is large and positive","R equals k"],
         "ans": 2, "exp": "Large positive R → corner. Large negative R → edge. |R| ≈ 0 → flat region. Typical k = 0.04."},
        {"q": "Hu moments are useful because they are invariant to:",
         "opts": ["Noise only","Rotation, scale, and translation","Colour changes","Frequency shifts"],
         "ans": 1, "exp": "The 7 Hu moments remain constant under rotation, scaling, and translation — ideal shape fingerprints."},
    ],
}

def render_quiz(module_key: str, session_prefix: str = "quiz"):
    """Render interactive MCQ quiz. Returns score or None if not yet completed."""
    questions = QUIZ_BANK.get(module_key, [])
    if not questions:
        st.info("No quiz available for this module yet.")
        return None

    score_key   = f"{session_prefix}_score"
    done_key    = f"{session_prefix}_done"
    answers_key = f"{session_prefix}_answers"

    if done_key not in st.session_state:
        st.session_state[done_key]    = False
        st.session_state[score_key]   = 0
        st.session_state[answers_key] = {}

    if st.session_state[done_key]:
        score = st.session_state[score_key]
        total = len(questions)
        pct   = score / total * 100
        colour = "#22c55e" if pct>=70 else "#f59e0b" if pct>=40 else "#ef4444"
        emoji  = "🏆" if pct>=70 else "📚" if pct>=40 else "💡"
        msg    = ("Excellent! You've mastered this module." if pct>=70
                  else "Good effort — review theory and try again." if pct>=40
                  else "Keep studying — read the theory boxes carefully.")

        st.markdown(f"""
        <div style="background:{colour}18;border:2px solid {colour};border-radius:10px;
                    padding:20px;text-align:center;margin:12px 0">
          <div style="font-size:2.2rem;margin-bottom:8px">{emoji}</div>
          <div style="font-size:1.4rem;font-weight:700;color:{colour}">
            {score}/{total} — {pct:.0f}%
          </div>
          <div style="font-size:0.88rem;color:#555;margin-top:6px">{msg}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("#### Detailed Review")
        for i, q in enumerate(questions):
            user_idx = st.session_state[answers_key].get(i, -1)
            correct  = q["ans"]
            is_right = user_idx == correct
            bg    = "#f0fdf4" if is_right else "#fef2f2"
            bdr   = "#22c55e" if is_right else "#ef4444"
            prefix = "✅" if is_right else "❌"
            user_txt = q["opts"][user_idx] if user_idx >= 0 else "Not answered"
            st.markdown(f"""
            <div style="background:{bg};border-left:4px solid {bdr};border-radius:0 8px 8px 0;
                        padding:12px 16px;margin:8px 0">
              <div style="font-weight:600;margin-bottom:6px;color:#1a1a1a">Q{i+1}: {q['q']}</div>
              <div style="font-size:0.85rem;color:#444">
                {prefix} Your answer: <b>{user_txt}</b>
                {'  |  Correct: <b>' + q['opts'][correct] + '</b>' if not is_right else ''}
              </div>
              <div style="font-size:0.82rem;color:#2d3a6b;margin-top:8px;padding:8px 12px;
                          background:#f0f4ff;border-radius:6px;border-left:3px solid #4f6ef7">
                💡 {q['exp']}
              </div>
            </div>""", unsafe_allow_html=True)

        if st.button("🔄 Retake Quiz", key=f"{session_prefix}_retry"):
            st.session_state[done_key]    = False
            st.session_state[score_key]   = 0
            st.session_state[answers_key] = {}
            st.rerun()
        return score

    st.markdown(f"**{module_key} — {len(questions)} questions · Select one answer per question**")
    with st.form(key=f"{session_prefix}_form"):
        answers = {}
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}: {q['q']}**")
            answers[i] = st.radio(
                label="", options=q["opts"],
                key=f"{session_prefix}_q{i}", index=None,
                label_visibility="collapsed"
            )
            st.markdown("")

        if st.form_submit_button("✅ Submit Answers"):
            score = 0
            ans_idx = {}
            for i, q in enumerate(questions):
                chosen = answers.get(i)
                idx = q["opts"].index(chosen) if chosen in q["opts"] else -1
                ans_idx[i] = idx
                if idx == q["ans"]: score += 1
            st.session_state[done_key]    = True
            st.session_state[score_key]   = score
            st.session_state[answers_key] = ans_idx
            st.rerun()
    return None
