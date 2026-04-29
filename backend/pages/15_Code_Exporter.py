import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
from utils.theme import inject, page_header, theory_card, code_card
from utils.helpers import upload_image, to_gray, normalize_display, comparison_slider

inject("Code Exporter", "💻")


page_header("Python Code Exporter",
            "APPLY ANY DIP OPERATION AND GET THE EXACT OPENCV/NUMPY CODE THAT PRODUCED IT", "💻", "#f87171")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


img_rgb = upload_image("code_up")
gray    = to_gray(img_rgb)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💻 Export Settings")
include_imports   = st.sidebar.checkbox("Include import statements", True)
include_comments  = st.sidebar.checkbox("Include comments", True)
include_load_save = st.sidebar.checkbox("Include load/save code", True)

theory_card(
    "This tool generates production-ready OpenCV Python code for every operation. "
    "The exact parameter values you chose are embedded in the code. "
    "Copy the code into any Python file or Jupyter notebook and it will run immediately."
)

# ── Operation categories ───────────────────────────────────────────────────────
category = st.selectbox("Category", [
    "Spatial Filters",
    "Histogram Processing",
    "Edge Detection",
    "Morphological Operations",
    "Frequency Domain Filters",
    "Intensity Transforms",
    "Colour Space Conversions",
    "Noise & Restoration",
    "Segmentation",
    "Feature Detection",
])

def make_code(op_name, params_dict, core_lines, imports=None, before_core="", after_core=""):
    """Assemble a clean exportable Python script."""
    lines = []
    if include_imports:
        base_imports = ["import cv2", "import numpy as np", "import matplotlib.pyplot as plt"]
        if imports:
            base_imports += imports
        lines += base_imports + [""]
    if include_load_save:
        lines += [
            '# ── Load image ──────────────────────────────────────',
            'img_bgr  = cv2.imread("your_image.jpg")',
            'img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)',
            'img_rgb  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)',
            "",
        ]
    if include_comments:
        lines += [f"# ── {op_name} ──────────────────────────────────────"]
        if params_dict:
            lines += ["# Parameters: " + ", ".join(f"{k}={v}" for k,v in params_dict.items())]
    if before_core:
        lines += [before_core, ""]
    lines += core_lines
    if after_core:
        lines += ["", after_core]
    if include_load_save:
        lines += [
            "",
            "# ── Save result ────────────────────────────────────",
            'cv2.imwrite("result.png", result if len(result.shape)==2 else cv2.cvtColor(result, cv2.COLOR_RGB2BGR))',
            "",
            "# ── Display ────────────────────────────────────────",
            'plt.figure(figsize=(10,4))',
            'plt.subplot(1,2,1); plt.imshow(img_gray, cmap="gray"); plt.title("Original"); plt.axis("off")',
            'plt.subplot(1,2,2); plt.imshow(result, cmap="gray"); plt.title(f"{op_name}"); plt.axis("off")',
            'plt.tight_layout(); plt.show()',
        ]
    return "\n".join(lines)

# ── Build UI per category ──────────────────────────────────────────────────────
before_img = gray.copy()
after_img  = gray.copy()
generated_code = ""

if category == "Spatial Filters":
    op = st.selectbox("Filter", ["Gaussian Blur","Median Filter","Bilateral Filter","Box Filter","Sharpen (Unsharp Mask)"])
    if op == "Gaussian Blur":
        k = st.slider("Kernel size", 3, 31, 9, step=2)
        s = st.slider("Sigma", 0.5, 10.0, 2.0)
        after_img = cv2.GaussianBlur(gray, (k,k), s)
        generated_code = make_code(op, {"ksize":k,"sigma":s}, [
            f"result = cv2.GaussianBlur(img_gray, ({k}, {k}), {s})",
        ])
    elif op == "Median Filter":
        k = st.slider("Kernel size", 3, 21, 5, step=2)
        after_img = cv2.medianBlur(gray, k)
        generated_code = make_code(op, {"ksize":k}, [
            f"result = cv2.medianBlur(img_gray, {k})",
        ])
    elif op == "Bilateral Filter":
        d  = st.slider("Diameter", 3, 21, 9, step=2)
        sc = st.slider("Sigma colour", 10, 150, 75)
        ss = st.slider("Sigma space",  10, 150, 75)
        after_img = cv2.bilateralFilter(gray, d, sc, ss)
        generated_code = make_code(op, {"d":d,"sc":sc,"ss":ss}, [
            f"result = cv2.bilateralFilter(img_gray, {d}, {sc}, {ss})",
        ])
    elif op == "Box Filter":
        k = st.slider("Kernel size", 3, 31, 9, step=2)
        after_img = cv2.blur(gray, (k,k))
        generated_code = make_code(op, {"ksize":k}, [
            f"result = cv2.blur(img_gray, ({k}, {k}))",
        ])
    else:
        k = st.slider("Kernel size", 3, 31, 9, step=2)
        s = st.slider("Sigma", 0.5, 10.0, 2.0)
        a = st.slider("Amount α", 0.5, 3.0, 1.5)
        blur = cv2.GaussianBlur(gray, (k,k), s)
        after_img = np.clip(gray.astype(float)+a*(gray.astype(float)-blur.astype(float)),0,255).astype(np.uint8)
        generated_code = make_code(op, {"ksize":k,"sigma":s,"amount":a}, [
            f"blurred  = cv2.GaussianBlur(img_gray, ({k}, {k}), {s})",
            f"result   = np.clip(img_gray.astype(float) + {a}*(img_gray.astype(float) - blurred), 0, 255).astype(np.uint8)",
        ])

elif category == "Histogram Processing":
    op = st.selectbox("Method", ["Histogram Equalisation","CLAHE","Histogram Stretch"])
    if op == "Histogram Equalisation":
        after_img = cv2.equalizeHist(gray)
        generated_code = make_code(op, {}, ["result = cv2.equalizeHist(img_gray)"])
    elif op == "CLAHE":
        clip = st.slider("Clip limit", 1.0, 10.0, 2.0)
        tile = st.slider("Tile size",  2, 16, 8)
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile,tile))
        after_img = clahe.apply(gray)
        generated_code = make_code(op, {"clip":clip,"tile":tile}, [
            f"clahe  = cv2.createCLAHE(clipLimit={clip}, tileGridSize=({tile}, {tile}))",
            "result = clahe.apply(img_gray)",
        ])
    else:
        mn, mx = int(gray.min()), int(gray.max())
        after_img = np.clip((gray.astype(float)-mn)/(mx-mn)*255,0,255).astype(np.uint8)
        generated_code = make_code(op, {"min":mn,"max":mx}, [
            "mn, mx = img_gray.min(), img_gray.max()",
            "result = np.clip((img_gray.astype(float) - mn) / (mx - mn) * 255, 0, 255).astype(np.uint8)",
        ])

elif category == "Edge Detection":
    op = st.selectbox("Detector", ["Canny","Sobel X","Sobel Y","Sobel Combined","Laplacian","LoG","Prewitt","Roberts"])
    if op == "Canny":
        t1 = st.slider("Low T",  10, 200, 50)
        t2 = st.slider("High T", 50, 400, 150)
        after_img = cv2.Canny(gray, t1, t2)
        generated_code = make_code(op, {"t1":t1,"t2":t2}, [f"result = cv2.Canny(img_gray, {t1}, {t2})"])
    elif op == "Sobel X":
        k = st.select_slider("Kernel", [1,3,5,7], 3)
        after_img = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=k))
        generated_code = make_code(op, {"ksize":k}, [
            f"sobel_x = cv2.Sobel(img_gray, cv2.CV_32F, 1, 0, ksize={k})",
            "result  = cv2.convertScaleAbs(sobel_x)",
        ])
    elif op == "Sobel Y":
        k = st.select_slider("Kernel", [1,3,5,7], 3)
        after_img = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=k))
        generated_code = make_code(op, {"ksize":k}, [
            f"sobel_y = cv2.Sobel(img_gray, cv2.CV_32F, 0, 1, ksize={k})",
            "result  = cv2.convertScaleAbs(sobel_y)",
        ])
    elif op == "Sobel Combined":
        sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        after_img = cv2.convertScaleAbs(np.sqrt(sx**2+sy**2))
        generated_code = make_code(op, {}, [
            "sx     = cv2.Sobel(img_gray, cv2.CV_32F, 1, 0, ksize=3)",
            "sy     = cv2.Sobel(img_gray, cv2.CV_32F, 0, 1, ksize=3)",
            "result = cv2.convertScaleAbs(np.sqrt(sx**2 + sy**2))",
        ])
    elif op == "Laplacian":
        after_img = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_32F))
        generated_code = make_code(op, {}, ["result = cv2.convertScaleAbs(cv2.Laplacian(img_gray, cv2.CV_32F))"])
    elif op == "LoG":
        s = st.slider("Sigma", 0.5, 5.0, 1.5)
        smooth = cv2.GaussianBlur(gray, (0,0), s)
        after_img = cv2.convertScaleAbs(cv2.Laplacian(smooth, cv2.CV_32F))
        generated_code = make_code(op, {"sigma":s}, [
            f"smoothed = cv2.GaussianBlur(img_gray, (0, 0), {s})",
            "result   = cv2.convertScaleAbs(cv2.Laplacian(smoothed, cv2.CV_32F))",
        ])
    elif op == "Prewitt":
        kx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], np.float32)
        ky = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], np.float32)
        after_img = cv2.convertScaleAbs(np.sqrt(cv2.filter2D(gray.astype(np.float32),-1,kx)**2+cv2.filter2D(gray.astype(np.float32),-1,ky)**2))
        generated_code = make_code(op, {}, [
            "kx     = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)",
            "ky     = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=np.float32)",
            "px     = cv2.filter2D(img_gray.astype(np.float32), -1, kx)",
            "py     = cv2.filter2D(img_gray.astype(np.float32), -1, ky)",
            "result = cv2.convertScaleAbs(np.sqrt(px**2 + py**2))",
        ])
    else:  # Roberts
        k1 = np.array([[1,0],[0,-1]], np.float32)
        k2 = np.array([[0,1],[-1,0]], np.float32)
        r1 = cv2.filter2D(gray.astype(np.float32),-1,k1)
        r2 = cv2.filter2D(gray.astype(np.float32),-1,k2)
        after_img = cv2.convertScaleAbs(np.sqrt(r1**2+r2**2))
        generated_code = make_code(op, {}, [
            "k1     = np.array([[1,0],[0,-1]], dtype=np.float32)",
            "k2     = np.array([[0,1],[-1,0]], dtype=np.float32)",
            "r1     = cv2.filter2D(img_gray.astype(np.float32), -1, k1)",
            "r2     = cv2.filter2D(img_gray.astype(np.float32), -1, k2)",
            "result = cv2.convertScaleAbs(np.sqrt(r1**2 + r2**2))",
        ])

elif category == "Morphological Operations":
    op = st.selectbox("Operation", ["Erosion","Dilation","Opening","Closing","Gradient","Top-Hat","Black-Hat","Skeletonisation"])
    k  = st.slider("SE size", 3, 31, 7, step=2)
    se = st.radio("SE shape", ["Ellipse","Rectangle","Cross"], horizontal=True)
    se_map = {"Ellipse":cv2.MORPH_ELLIPSE,"Rectangle":cv2.MORPH_RECT,"Cross":cv2.MORPH_CROSS}
    kernel = cv2.getStructuringElement(se_map[se], (k,k))
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    before_img = binary
    morph_map  = {"Erosion":cv2.MORPH_ERODE,"Dilation":cv2.MORPH_DILATE,"Opening":cv2.MORPH_OPEN,
                  "Closing":cv2.MORPH_CLOSE,"Gradient":cv2.MORPH_GRADIENT,"Top-Hat":cv2.MORPH_TOPHAT,"Black-Hat":cv2.MORPH_BLACKHAT}
    if op == "Skeletonisation":
        img_sk = binary.copy(); skel = np.zeros_like(img_sk); ks = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
        for _ in range(50):
            e=cv2.erode(img_sk,ks); t=cv2.dilate(e,ks); skel=cv2.bitwise_or(skel,cv2.subtract(img_sk,t)); img_sk=e
            if cv2.countNonZero(img_sk)==0: break
        after_img = skel
        generated_code = make_code(op, {"SE":f"{k}×{k}"}, [
            '_, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)',
            'img_sk   = binary.copy()',
            'skel     = np.zeros_like(img_sk)',
            'kernel   = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))',
            'while True:',
            '    eroded = cv2.erode(img_sk, kernel)',
            '    temp   = cv2.dilate(eroded, kernel)',
            '    skel   = cv2.bitwise_or(skel, cv2.subtract(img_sk, temp))',
            '    img_sk = eroded',
            '    if cv2.countNonZero(img_sk) == 0: break',
            'result = skel',
        ])
    else:
        after_img = cv2.morphologyEx(binary, morph_map[op], kernel)
        se_const  = {"Ellipse":"cv2.MORPH_ELLIPSE","Rectangle":"cv2.MORPH_RECT","Cross":"cv2.MORPH_CROSS"}[se]
        mo_const  = {"Erosion":"cv2.MORPH_ERODE","Dilation":"cv2.MORPH_DILATE","Opening":"cv2.MORPH_OPEN",
                     "Closing":"cv2.MORPH_CLOSE","Gradient":"cv2.MORPH_GRADIENT",
                     "Top-Hat":"cv2.MORPH_TOPHAT","Black-Hat":"cv2.MORPH_BLACKHAT"}[op]
        generated_code = make_code(op, {"SE":f"{k}×{k}","shape":se}, [
            '_, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)',
            f'kernel = cv2.getStructuringElement({se_const}, ({k}, {k}))',
            f'result = cv2.morphologyEx(binary, {mo_const}, kernel)',
        ])

elif category == "Frequency Domain Filters":
    ftype = st.selectbox("Filter", ["Gaussian LP","Gaussian HP","Butterworth LP","Butterworth HP","Ideal LP","Ideal HP"])
    D0    = st.slider("Cut-off D₀", 5, 100, 30)
    rows,cols = gray.shape; crow,ccol=rows//2,cols//2
    Y,X = np.ogrid[:rows,:cols]; D=np.sqrt((Y-crow)**2+(X-ccol)**2)
    if ftype=="Gaussian LP":   H=np.exp(-(D**2)/(2*D0**2))
    elif ftype=="Gaussian HP":  H=1-np.exp(-(D**2)/(2*D0**2))
    elif ftype=="Butterworth LP": n=st.slider("Order",1,8,2); H=1/(1+(D/D0)**(2*n))
    elif ftype=="Butterworth HP": n=st.slider("Order",1,8,2); H=1-1/(1+(D/D0)**(2*n))
    elif ftype=="Ideal LP":     H=(D<=D0).astype(float)
    else:                       H=(D>D0).astype(float)
    F     = np.fft.fftshift(np.fft.fft2(gray.astype(float)))
    after_img = normalize_display(np.abs(np.fft.ifft2(np.fft.ifftshift(F*H))))
    generated_code = make_code(ftype, {"D0":D0}, [
        "rows, cols    = img_gray.shape",
        "crow, ccol    = rows // 2, cols // 2",
        "Y, X          = np.ogrid[:rows, :cols]",
        "D             = np.sqrt((Y - crow)**2 + (X - ccol)**2)",
        f"H             = np.exp(-(D**2) / (2 * {D0}**2))  # Gaussian LP — change formula for other types",
        "F             = np.fft.fftshift(np.fft.fft2(img_gray.astype(float)))",
        "filtered      = np.fft.ifft2(np.fft.ifftshift(F * H))",
        "result        = np.abs(filtered)",
        "result        = ((result - result.min()) / (result.max() - result.min()) * 255).astype(np.uint8)",
    ])

elif category == "Intensity Transforms":
    op = st.selectbox("Transform", ["Gamma","Log","Negative","Threshold","Histogram Stretch"])
    if op == "Gamma":
        g = st.slider("γ", 0.1, 4.0, 1.5)
        lut = np.array([((i/255.0)**g)*255 for i in range(256)], np.uint8)
        after_img = cv2.LUT(gray, lut)
        generated_code = make_code(op, {"gamma":g}, [
            f"gamma = {g}",
            "lut    = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)], dtype=np.uint8)",
            "result = cv2.LUT(img_gray, lut)",
        ])
    elif op == "Log":
        c = st.slider("c", 1, 50, 10)
        after_img = normalize_display(c * np.log1p(gray.astype(float)))
        generated_code = make_code(op, {"c":c}, [
            f"c      = {c}",
            "log_img = c * np.log1p(img_gray.astype(float))",
            "result  = ((log_img / log_img.max()) * 255).astype(np.uint8)",
        ])
    elif op == "Negative":
        after_img = 255 - gray
        generated_code = make_code(op, {}, ["result = 255 - img_gray"])
    elif op == "Threshold":
        T = st.slider("T", 0, 255, 127)
        _, after_img = cv2.threshold(gray, T, 255, cv2.THRESH_BINARY)
        generated_code = make_code(op, {"T":T}, [f"_, result = cv2.threshold(img_gray, {T}, 255, cv2.THRESH_BINARY)"])
    else:
        mn,mx = int(gray.min()), int(gray.max())
        after_img = np.clip((gray.astype(float)-mn)/(mx-mn)*255,0,255).astype(np.uint8)
        generated_code = make_code(op, {}, [
            "mn, mx = img_gray.min(), img_gray.max()",
            "result = np.clip((img_gray.astype(float) - mn) / (mx - mn) * 255, 0, 255).astype(np.uint8)",
        ])

elif category == "Colour Space Conversions":
    op = st.selectbox("Conversion", ["RGB→HSV","RGB→LAB","RGB→YCbCr","Greyscale","Pseudo-colour (Jet)"])
    if op == "RGB→HSV":
        after_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)[:,:,0]
        generated_code = make_code(op, {}, [
            "hsv      = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)",
            "result   = hsv[:, :, 0]  # Hue channel",
        ])
    elif op == "RGB→LAB":
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        after_img = lab[:,:,0]
        generated_code = make_code(op, {}, [
            "lab    = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)",
            "result = lab[:, :, 0]  # L* (lightness) channel",
        ])
    elif op == "RGB→YCbCr":
        ycbcr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
        after_img = ycbcr[:,:,0]
        generated_code = make_code(op, {}, [
            "ycbcr  = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)",
            "result = ycbcr[:, :, 0]  # Y (luma) channel",
        ])
    elif op == "Greyscale":
        after_img = gray
        generated_code = make_code(op, {}, ["result = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)"])
    else:
        pseudo = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        after_img = cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB)[:,:,0]
        generated_code = make_code(op, {}, [
            "pseudo = cv2.applyColorMap(img_gray, cv2.COLORMAP_JET)",
            "result = cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB)",
        ])

elif category == "Noise & Restoration":
    op = st.selectbox("Operation", ["Add Gaussian Noise","Add Salt & Pepper","Wiener Filter","Inverse Filter"])
    if op == "Add Gaussian Noise":
        sigma = st.slider("σ", 5, 80, 20)
        after_img = np.clip(gray.astype(float)+np.random.normal(0,sigma,gray.shape),0,255).astype(np.uint8)
        generated_code = make_code(op, {"sigma":sigma}, [
            f"noise  = np.random.normal(0, {sigma}, img_gray.shape)",
            "result = np.clip(img_gray.astype(float) + noise, 0, 255).astype(np.uint8)",
        ])
    elif op == "Add Salt & Pepper":
        prob = st.slider("Probability", 0.01, 0.3, 0.05)
        noisy = gray.copy(); mask=np.random.rand(*gray.shape)
        noisy[mask<prob/2]=0; noisy[mask>1-prob/2]=255; after_img=noisy
        generated_code = make_code(op, {"prob":prob}, [
            f"prob   = {prob}",
            "noisy  = img_gray.copy()",
            "mask   = np.random.rand(*img_gray.shape)",
            "noisy[mask < prob / 2]     = 0",
            "noisy[mask > 1 - prob / 2] = 255",
            "result = noisy",
        ])
    elif op == "Wiener Filter":
        K = st.slider("K", 0.001, 0.5, 0.01, format="%.3f")
        psf=np.zeros_like(gray.astype(float)); psf[gray.shape[0]//2,:10]=1/10
        H2=np.fft.fft2(psf); G=H2*np.fft.fft2(gray.astype(float))
        G+=np.fft.fft2(np.random.normal(0,10,gray.shape))
        Hw=np.conj(H2)/(np.abs(H2)**2+K)
        after_img=normalize_display(np.abs(np.fft.ifft2(Hw*G)))
        generated_code = make_code(op, {"K":K}, [
            "# Create motion blur PSF (10-pixel horizontal)",
            "psf     = np.zeros_like(img_gray.astype(float))",
            "psf[img_gray.shape[0]//2, :10] = 1.0 / 10",
            "H       = np.fft.fft2(psf)",
            "G       = H * np.fft.fft2(img_gray.astype(float))",
            f"K       = {K}  # noise-to-signal ratio",
            "H_w     = np.conj(H) / (np.abs(H)**2 + K)",
            "restored = np.abs(np.fft.ifft2(H_w * G))",
            "result  = ((restored / restored.max()) * 255).astype(np.uint8)",
        ])
    else:
        thresh = st.slider("H threshold", 0.001, 0.5, 0.05)
        psf=np.zeros_like(gray.astype(float)); psf[gray.shape[0]//2,:10]=1/10
        H2=np.fft.fft2(psf); G=H2*np.fft.fft2(gray.astype(float))
        H_inv=np.where(np.abs(H2)>thresh,1.0/H2,0)
        after_img=normalize_display(np.abs(np.fft.ifft2(np.fft.fft2(np.abs(np.fft.ifft2(G)))*H_inv)))
        generated_code = make_code(op, {"threshold":thresh}, [
            "psf     = np.zeros_like(img_gray.astype(float))",
            "psf[img_gray.shape[0]//2, :10] = 1.0 / 10",
            "H       = np.fft.fft2(psf)",
            f"H_inv   = np.where(np.abs(H) > {thresh}, 1.0 / H, 0)  # truncated inverse",
            "G       = H * np.fft.fft2(img_gray.astype(float))",
            "result  = np.abs(np.fft.ifft2(np.fft.fft2(np.abs(np.fft.ifft2(G))) * H_inv))",
            "result  = ((result / result.max()) * 255).astype(np.uint8)",
        ])

elif category == "Segmentation":
    op = st.selectbox("Method", ["Otsu Threshold","Adaptive Threshold","Watershed","Contour Detection"])
    if op == "Otsu Threshold":
        T, after_img = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        generated_code = make_code(op, {"auto_T":int(T)}, [
            "T, result = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)",
            "print(f'Otsu threshold: {T}')",
        ])
    elif op == "Adaptive Threshold":
        block=st.slider("Block",3,99,11,step=2); C=st.slider("C",-30,30,2)
        after_img=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,block,C)
        generated_code = make_code(op, {"block":block,"C":C}, [
            f"result = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,",
            f"                                cv2.THRESH_BINARY, {block}, {C})",
        ])
    elif op == "Watershed":
        _, thresh_w = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        kernel_w=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        sure_bg=cv2.dilate(thresh_w,kernel_w,iterations=3)
        dt=cv2.distanceTransform(thresh_w,cv2.DIST_L2,5)
        _,sure_fg=cv2.threshold(dt,0.5*dt.max(),255,0)
        unknown=cv2.subtract(sure_bg,sure_fg.astype(np.uint8))
        _,markers=cv2.connectedComponents(sure_fg.astype(np.uint8))
        markers=markers+1; markers[unknown==255]=0
        overlay=cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
        markers_ws=cv2.watershed(overlay,markers)
        overlay[markers_ws==-1]=[255,100,0]
        after_img=overlay[:,:,0]
        generated_code = make_code(op, {}, [
            "_, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)",
            "kernel    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))",
            "sure_bg   = cv2.dilate(thresh, kernel, iterations=3)",
            "dist      = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)",
            "_, sure_fg = cv2.threshold(dist, 0.5 * dist.max(), 255, 0)",
            "unknown   = cv2.subtract(sure_bg, sure_fg.astype(np.uint8))",
            "_, markers = cv2.connectedComponents(sure_fg.astype(np.uint8))",
            "markers   = markers + 1",
            "markers[unknown == 255] = 0",
            "img_rgb_for_ws = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)",
            "cv2.watershed(img_rgb_for_ws, markers)",
            "img_rgb_for_ws[markers == -1] = [0, 0, 255]  # red boundaries",
            "result = img_rgb_for_ws",
        ])
    else:
        _, binary_c = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        contours,_  = cv2.findContours(binary_c,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        overlay     = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
        cv2.drawContours(overlay,contours,-1,(0,200,100),2)
        after_img   = overlay[:,:,0]
        generated_code = make_code(op, {"n_contours":len(contours)}, [
            "_, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)",
            "contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)",
            "result = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)",
            "cv2.drawContours(result, contours, -1, (0, 200, 100), 2)",
            f"print(f'Found {{len(contours)}} contours')",
        ])

else:  # Feature Detection
    op = st.selectbox("Detector", ["Harris Corners","Shi-Tomasi","FAST Keypoints","Hough Lines","Hough Circles"])
    overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    if op == "Harris Corners":
        dst = cv2.cornerHarris(gray,2,3,0.04); dst=cv2.dilate(dst,None)
        overlay[dst>0.01*dst.max()]=[255,50,50]; after_img=overlay[:,:,0]
        generated_code = make_code(op, {"k":0.04}, [
            "dst    = cv2.cornerHarris(img_gray, 2, 3, 0.04)",
            "dst    = cv2.dilate(dst, None)",
            "result = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)",
            "result[dst > 0.01 * dst.max()] = [0, 0, 255]  # red corners",
        ])
    elif op == "Shi-Tomasi":
        corners = cv2.goodFeaturesToTrack(gray,100,0.01,10)
        if corners is not None:
            for c in np.int0(corners): cv2.circle(overlay,(c.ravel()[0],c.ravel()[1]),4,[255,80,0],-1)
        after_img=overlay[:,:,0]
        generated_code = make_code(op, {"max":100,"quality":0.01,"minDist":10}, [
            "corners = cv2.goodFeaturesToTrack(img_gray, maxCorners=100, qualityLevel=0.01, minDistance=10)",
            "result  = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)",
            "if corners is not None:",
            "    for c in np.int0(corners):",
            "        x, y = c.ravel()",
            "        cv2.circle(result, (x, y), 4, (0, 165, 255), -1)",
        ])
    elif op == "FAST Keypoints":
        fast = cv2.FastFeatureDetector_create(threshold=10)
        kps  = fast.detect(gray)
        for kp in kps: cv2.circle(overlay,(int(kp.pt[0]),int(kp.pt[1])),3,[0,200,100],-1)
        after_img=overlay[:,:,0]
        generated_code = make_code(op, {"threshold":10}, [
            "fast = cv2.FastFeatureDetector_create(threshold=10, nonmaxSuppression=True)",
            "kps  = fast.detect(img_gray)",
            "result = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)",
            "for kp in kps:",
            "    x, y = int(kp.pt[0]), int(kp.pt[1])",
            "    cv2.circle(result, (x, y), 3, (0, 200, 100), -1)",
        ])
    elif op == "Hough Lines":
        edges = cv2.Canny(gray,50,150)
        lines = cv2.HoughLinesP(edges,1,np.pi/180,50,minLineLength=30,maxLineGap=10)
        if lines is not None:
            for l in lines: cv2.line(overlay,(l[0][0],l[0][1]),(l[0][2],l[0][3]),(255,150,0),2)
        after_img=overlay[:,:,0]
        generated_code = make_code(op, {"threshold":50,"minLen":30,"maxGap":10}, [
            "edges = cv2.Canny(img_gray, 50, 150)",
            "lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)",
            "result = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)",
            "if lines is not None:",
            "    for line in lines:",
            "        x1,y1,x2,y2 = line[0]",
            "        cv2.line(result, (x1,y1), (x2,y2), (0,165,255), 2)",
        ])
    else:
        circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1.5,30,param1=80,param2=30,minRadius=10,maxRadius=60)
        if circles is not None:
            for (x,y,r) in np.round(circles[0]).astype(int):
                cv2.circle(overlay,(x,y),r,(0,200,255),2); cv2.circle(overlay,(x,y),2,(255,100,0),3)
        after_img=overlay[:,:,0]
        generated_code = make_code(op, {"dp":1.5,"minDist":30}, [
            "circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, dp=1.5, minDist=30,",
            "                            param1=80, param2=30, minRadius=10, maxRadius=60)",
            "result  = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)",
            "if circles is not None:",
            "    circles = np.round(circles[0]).astype(int)",
            "    for (x, y, r) in circles:",
            "        cv2.circle(result, (x, y), r, (0, 200, 255), 2)",
        ])

# ── Display results + code ─────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Before**")
    st.image(np.clip(before_img,0,255).astype(np.uint8), use_container_width=True, clamp=True)
with col2:
    st.markdown("**After**")
    st.image(np.clip(after_img,0,255).astype(np.uint8), use_container_width=True, clamp=True)

st.markdown("---")
st.markdown("### 💻 Generated Python Code")
st.markdown("""
<div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.3);
            border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:0.83rem;color:#fca5a5">
  ✅ Copy this code into any Python file. Install requirements: <code>pip install opencv-python numpy matplotlib pillow</code>
</div>""", unsafe_allow_html=True)

st.code(generated_code, language="python")

st.download_button(
    "⬇ Download as .py file",
    generated_code,
    f"dip_{category.replace(' ','_').lower()[:20]}.py",
    "text/x-python"
)
