from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import cv2
import numpy as np
import io
import hashlib
import json
import os
from pathlib import Path

app = FastAPI(title="DIP Simulator API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Local user store (JSON file, auto-seeded) ──────────────────────────────────
_USERS_FILE = Path(__file__).parent / "users.json"

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _load_users() -> list[dict]:
    if _USERS_FILE.exists():
        try:
            return json.loads(_USERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Seed default accounts
    defaults = [
        {"email": "admin@dip.edu",   "password_hash": _hash("dip2024"),  "username": "admin",   "role": "admin"},
        {"email": "student@dip.edu", "password_hash": _hash("learn123"), "username": "student", "role": "student"},
        {"email": "guest@dip.edu",   "password_hash": _hash("guest"),    "username": "guest",   "role": "guest"},
    ]
    _USERS_FILE.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
    return defaults

def _save_users(users: list[dict]):
    _USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")

# ── Auth request models ────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str = ""
    role: str = "student"

def read_imagefile(contents: bytes) -> np.ndarray:
    try:
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

def encode_image(img: np.ndarray, ext: str = ".jpg") -> bytes:
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if len(img.shape) == 3 else img
    success, encoded_img = cv2.imencode(ext, img_bgr)
    if not success:
        raise HTTPException(status_code=500, detail="Could not encode image")
    return encoded_img.tobytes()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "4.0"}

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
def auth_login(body: LoginRequest):
    users = _load_users()
    email = body.email.strip().lower()
    pw_hash = _hash(body.password)
    user = next((u for u in users if u["email"] == email and u["password_hash"] == pw_hash), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {
        "email":    user["email"],
        "username": user.get("username", ""),
        "role":     user.get("role", "student"),
    }

@app.post("/api/auth/register")
def auth_register(body: RegisterRequest):
    if "@" not in body.email or "." not in body.email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
    if len(body.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    users = _load_users()
    email = body.email.strip().lower()
    if any(u["email"] == email for u in users):
        raise HTTPException(status_code=409, detail="Email already registered. Please sign in.")
    users.append({
        "email":         email,
        "password_hash": _hash(body.password),
        "username":      body.username or email.split("@")[0],
        "role":          body.role if body.role in ("student", "guest") else "student",
    })
    _save_users(users)
    return {"message": "Account created successfully! You can now sign in."}

# --- DISCOVERY ROUTES ---
@app.get("/api/modules")
def get_modules():
    return {
        "modules": [
            {
                "id": "m1", "number": 1, "title": "Image Fundamentals", "subtitle": "Digital imaging basics & pixel operations",
                "icon": "🖼️", "color": "#4361ee", "streamlit_page": "Module1_Fundamentals",
                "topics": ["Pixels", "Sampling", "Quantization", "Linear Ops"]
            },
            {
                "id": "m2", "number": 2, "title": "Spatial & Frequency", "subtitle": "Filtering, transforms & enhancements",
                "icon": "🌊", "color": "#b44fff", "streamlit_page": "Module2_SpatialFrequency",
                "topics": ["Histograms", "Smoothing", "DFT", "LPF/HPF"]
            },
            {
                "id": "m3", "number": 3, "title": "Image Restoration", "subtitle": "Noise models & degradation filters",
                "icon": "🔧", "color": "#4cc9f0", "streamlit_page": "Module3_Restoration",
                "topics": ["Noise", "Inverse Filter", "Wiener", "CLS"]
            },
            {
                "id": "m4", "number": 4, "title": "Color & Morphology", "subtitle": "Color models & shape processing",
                "icon": "🎨", "color": "#f8961e", "streamlit_page": "Module4_ColorMorphology",
                "topics": ["HSV/RGB", "Dilation", "Erosion", "Hit-or-Miss"]
            },
            {
                "id": "m5", "number": 5, "title": "Image Segmentation", "subtitle": "Edges, corners & feature descriptors",
                "icon": "✂️", "color": "#ff3366", "streamlit_page": "Module5_Segmentation",
                "topics": ["Canny", "Hough", "Thresholding", "Moments"]
            }
        ]
    }

@app.get("/api/tools")
def get_tools():
    return {
        "tools": [
            {"id": "t2", "name": "Compare Slider", "desc": "Side-by-side comparison", "icon": "↔️", "color": "#4361ee", "page": "7_Comparison"},
            {"id": "t3", "name": "Super Res", "desc": "Bicubic upscaling", "icon": "✨", "color": "#b44fff", "page": "8_SuperResolution"},
            {"id": "t4", "name": "Lab Report", "desc": "Generate PDF records", "icon": "📄", "color": "#b44fff", "page": "9_LabReport"},
            {"id": "t5", "name": "DIP Quiz", "desc": "Test your knowledge", "icon": "🧠", "color": "#4cc9f0", "page": "10_Quiz"},
            {"id": "t6", "name": "Webcam Filter", "desc": "Live video processing", "icon": "📷", "color": "#4cc9f0", "page": "11_Webcam"},
            {"id": "t7", "name": "JPEG DCT", "desc": "Quantization demo", "icon": "📉", "color": "#f8961e", "page": "12_JPEG_Compression"},
            {"id": "t8", "name": "GIF Animator", "desc": "Sequence to animation", "icon": "🎞️", "color": "#f8961e", "page": "13_GIF_Animator"},
            {"id": "t9", "name": "Batch Processor", "desc": "Automated workflows", "icon": "⚡", "color": "#ff3366", "page": "14_Batch_Processing"},
            {"id": "t10", "name": "Code Exporter", "desc": "Python/MATLAB snippets", "icon": "💻", "color": "#ff3366", "page": "15_Code_Exporter"},
            {"id": "t20", "name": "Code Explainer", "desc": "Line-by-line analysis", "icon": "📖", "color": "#06d6a0", "page": "15_Code_Explainer"},
            {"id": "t11", "name": "Params Lab", "desc": "Interactive tuning", "icon": "🎛️", "color": "#4361ee", "page": "16_Parameter_Challenge"},
            {"id": "t12", "name": "Shape Analysis", "desc": "Feature descriptors", "icon": "📐", "color": "#b44fff", "page": "17_Feature_Descriptors"},
            {"id": "t13", "name": "Optical Flow", "desc": "Motion estimation", "icon": "🌊", "color": "#4cc9f0", "page": "18_Optical_Flow"},
            {"id": "t14", "name": "Session Log", "desc": "Recorder & history", "icon": "⏺️", "color": "#f8961e", "page": "19_Session_Recorder"},
            {"id": "t15", "name": "PSNR Metrics", "desc": "Quality assessment", "icon": "📏", "color": "#ff3366", "page": "20_Quality_Metrics"},
            {"id": "t16", "name": "Template Mat", "desc": "Pattern matching", "icon": "🎯", "color": "#4361ee", "page": "21_Template_Matching"},
            {"id": "t17", "name": "Doc Scanner", "desc": "Perspective & cleaning", "icon": "📠", "color": "#b44fff", "page": "22_Document_Scanner"},
            {"id": "t18", "name": "ELA Forensics", "desc": "Forgery detection", "icon": "🕵️", "color": "#4cc9f0", "page": "23_Forgery_Detector"},
            {"id": "t19", "name": "Stitching", "desc": "Panorama creation", "icon": "🧵", "color": "#f8961e", "page": "24_Image_Stitching"}
        ]
    }

# ── Statistics tracking ────────────────────────────────────────────────────────
_STATS_FILE = Path(__file__).parent / "stats.json"

def _load_stats():
    if _STATS_FILE.exists():
        try: return json.loads(_STATS_FILE.read_text(encoding="utf-8"))
        except: pass
    return {"total_processed": 0, "last_tool": "None", "recent_activity": [], "total_psnr": 0, "psnr_count": 0}

def _save_stats(s):
    _STATS_FILE.write_text(json.dumps(s, indent=2), encoding="utf-8")

def record_activity(tool_name: str, is_process: bool = False, psnr: float = None):
    s = _load_stats()
    if is_process:
        s["total_processed"] += 1
        if psnr is not None:
            s["total_psnr"] += psnr
            s["psnr_count"] += 1
    
    if tool_name:
        s["last_tool"] = tool_name
        act = f"Used {tool_name}"
        if is_process: act = f"Processed image in {tool_name}"
        
        # Keep unique recent activity
        if act not in s["recent_activity"]:
            s["recent_activity"].insert(0, act)
            s["recent_activity"] = s["recent_activity"][:5]
    
    _save_stats(s)

@app.get("/api/stats")
def get_stats():
    s = _load_stats()
    avg_psnr = 0
    if s.get("psnr_count", 0) > 0:
        avg_psnr = round(s["total_psnr"] / s["psnr_count"], 2)
        
    return {
        "modules": 5,
        "tools": 18,
        "pages": 24,
        "users": len(_load_users()),
        "total_processed": s["total_processed"],
        "last_tool": s["last_tool"],
        "recent_activity": s["recent_activity"],
        "avg_psnr": avg_psnr
    }

@app.post("/api/stats/record")
def post_record_activity(tool: str = Form(...)):
    record_activity(tool)
    return {"status": "ok"}

# --- MODULE 1 ROUTES ---
@app.post("/api/module1/pixel_inspector")
async def pixel_inspector(
    file: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    h, w = gray.shape
    if x < 1 or x >= w-1 or y < 1 or y >= h-1:
        raise HTTPException(status_code=400, detail="Coordinates out of bounds for 3x3 patch")

    val = int(gray[y, x])
    patch = gray[y-1:y+2, x-1:x+2].tolist()
    
    n4 = {
        "Up": int(gray[y-1, x]),
        "Down": int(gray[y+1, x]),
        "Left": int(gray[y, x-1]),
        "Right": int(gray[y, x+1]),
    }
    n8_extra = {
        "UL": int(gray[y-1, x-1]), "UR": int(gray[y-1, x+1]),
        "DL": int(gray[y+1, x-1]), "DR": int(gray[y+1, x+1]),
    }

    rgb_vals = None
    if len(img.shape) == 3:
        r, g, b = img[y, x]
        rgb_vals = {"R": int(r), "G": int(g), "B": int(b)}

    return {
        "intensity": val,
        "patch": patch,
        "n4": n4,
        "n8_extra": n8_extra,
        "rgb": rgb_vals
    }

@app.post("/api/module1/sampling_quantization")
async def sampling_quantization(
    file: UploadFile = File(...),
    factor: int = Form(...),
    bits: int = Form(...)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Sampling
    small = cv2.resize(gray, (max(1, gray.shape[1]//factor), max(1, gray.shape[0]//factor)), interpolation=cv2.INTER_NEAREST)
    restored = cv2.resize(small, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    # Quantization
    levels = 2 ** bits
    q_img = (restored // (256 // levels)) * (256 // levels)
    q_img = q_img.astype(np.uint8)
    record_activity("Sampling & Quantization", is_process=True)
    return Response(content=encode_image(q_img), media_type="image/jpeg")

@app.post("/api/module1/channels")
async def extract_channels(
    file: UploadFile = File(...),
    mode: str = Form(...) # 'rgb', 'hsv', 'ycbcr'
):
    img = read_imagefile(await file.read())
    
    if mode == "rgb":
        # Return base64 for multiple images, or we can just return one specific channel
        pass
        
    return Response(content=encode_image(img), media_type="image/jpeg")

@app.post("/api/module1/linear_operations")
async def linear_operations(
    file: UploadFile = File(...),
    op: str = Form(...),
    value: float = Form(...)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    out = gray
    if op == "brightness":
        out = np.clip(gray.astype(int) + int(value), 0, 255).astype(np.uint8)
    elif op == "contrast":
        out = np.clip(gray.astype(float) * value, 0, 255).astype(np.uint8)
    elif op == "gamma":
        lut = np.array([((i/255.0)**value)*255 for i in range(256)], dtype=np.uint8)
        out = cv2.LUT(gray, lut)
    elif op == "log":
        out = (value * np.log1p(gray.astype(float)))
        out = cv2.normalize(out, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    elif op == "negative":
        out = 255 - gray
    elif op == "threshold":
        _, out = cv2.threshold(gray, int(value), 255, cv2.THRESH_BINARY)
    
    record_activity(f"Linear: {op}", is_process=True)
    record_activity(f"Edges: {detector}", is_process=True)
    record_activity(f"Smoothing: {ftype}", is_process=True)
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module1/statistics")
async def image_statistics(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    
    return {
        "mean": float(gray.mean()),
        "std": float(gray.std()),
        "min": int(gray.min()),
        "max": int(gray.max()),
        "width": int(gray.shape[1]),
        "height": int(gray.shape[0]),
        "total_pixels": int(gray.size),
        "histogram": hist.tolist()
    }

# --- MODULE 2 ROUTES ---
@app.post("/api/module2/histogram")
async def histogram_processing(
    file: UploadFile = File(...),
    method: str = Form(...),
    clip: float = Form(2.0),
    tile: int = Form(8)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    if method == "global":
        eq = cv2.equalizeHist(gray)
    else:
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
        eq = clahe.apply(gray)
        
    return Response(content=encode_image(eq), media_type="image/jpeg")

@app.post("/api/module2/smoothing")
async def smoothing_filters(
    file: UploadFile = File(...),
    ftype: str = Form(...),
    ksize: int = Form(5),
    sigma: float = Form(1.5),
    d: int = Form(9),
    sc: int = Form(75),
    ss: int = Form(75),
    noise: bool = Form(False),
    noise_prob: float = Form(0.05)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    working = gray.copy()
    if noise:
        mask = np.random.rand(*gray.shape)
        working[mask < noise_prob/2] = 0
        working[mask > 1 - noise_prob/2] = 255
        
    if ftype == "average":
        out = cv2.blur(working, (ksize, ksize))
    elif ftype == "gaussian":
        out = cv2.GaussianBlur(working, (ksize, ksize), sigma)
    elif ftype == "median":
        out = cv2.medianBlur(working, ksize)
    else:
        out = cv2.bilateralFilter(working.astype(np.uint8), d, sc, ss)
        
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module2/sharpening")
async def sharpening_filters(
    file: UploadFile = File(...),
    stype: str = Form(...),
    weight: float = Form(1.0),
    sigma: float = Form(2.0),
    amount: float = Form(1.5),
    ksize: int = Form(3),
    boost: float = Form(2.0)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    if stype == "laplacian":
        lap = cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F)
        out = np.clip(gray.astype(float) - weight * lap, 0, 255).astype(np.uint8)
    elif stype == "unsharp":
        blurred = cv2.GaussianBlur(gray, (0,0), sigma)
        out = np.clip(gray.astype(float) + amount*(gray.astype(float) - blurred.astype(float)), 0, 255).astype(np.uint8)
    elif stype == "sobel":
        sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=ksize)
        sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=ksize)
        mag = np.sqrt(sx**2 + sy**2)
        out = np.clip(gray.astype(float) + weight * mag, 0, 255).astype(np.uint8)
    else: # high-boost
        blurred = cv2.GaussianBlur(gray, (0,0), 3)
        out = np.clip(boost * gray.astype(float) - (boost-1) * blurred.astype(float), 0, 255).astype(np.uint8)
        
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module2/dft")
async def dft_spectrum(
    file: UploadFile = File(...),
    view: str = Form(...) # magnitude or phase
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    f = np.fft.fft2(gray.astype(float))
    fshift = np.fft.fftshift(f)
    
    if view == "magnitude":
        magnitude = 20 * np.log(np.abs(fshift) + 1)
        out = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    else:
        phase = np.angle(fshift)
        out = cv2.normalize(phase, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module2/frequency_filter")
async def frequency_filters(
    file: UploadFile = File(...),
    ftype: str = Form(...),
    d0: float = Form(30),
    n: int = Form(2)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    rows, cols = gray.shape
    crow, ccol = rows//2, cols//2
    Y, X = np.ogrid[:rows, :cols]
    D = np.sqrt((Y - crow)**2 + (X - ccol)**2)
    
    H = None
    if ftype == "ideal_lpf":
        H = (D <= d0).astype(float)
    elif ftype == "ideal_hpf":
        H = (D > d0).astype(float)
    elif ftype == "gaussian_lpf":
        H = np.exp(-(D**2) / (2*d0**2))
    elif ftype == "gaussian_hpf":
        H = 1 - np.exp(-(D**2) / (2*d0**2))
    elif ftype == "butterworth_lpf":
        H = 1 / (1 + (D/d0)**(2*n))
    elif ftype == "butterworth_hpf":
        H = 1 - 1 / (1 + (D/d0)**(2*n))
        
    F = np.fft.fftshift(np.fft.fft2(gray.astype(float)))
    G = F * H
    g = np.abs(np.fft.ifft2(np.fft.ifftshift(G)))
    out = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return Response(content=encode_image(out), media_type="image/jpeg")

# --- MODULE 3 ROUTES ---
@app.post("/api/module3/noise")
async def apply_noise(
    file: UploadFile = File(...),
    ntype: str = Form(...),
    sigma: float = Form(20),
    prob: float = Form(0.05),
    a: float = Form(30),
    k: int = Form(2),
    scale: float = Form(10)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    
    out = gray.copy()
    if ntype == "Gaussian":
        out += np.random.normal(0, sigma, gray.shape)
    elif ntype == "Salt & Pepper":
        mask = np.random.rand(*gray.shape)
        out[mask < prob/2] = 0
        out[mask > 1-prob/2] = 255
    elif ntype == "Rayleigh":
        out += np.random.rayleigh(sigma, gray.shape)
    elif ntype == "Uniform":
        out += np.random.uniform(-a, a, gray.shape)
    elif ntype == "Erlang":
        out += np.random.gamma(k, scale, gray.shape)
        
    out = np.clip(out, 0, 255).astype(np.uint8)
    return Response(content=encode_image(out), media_type="image/jpeg")

def motion_blur_psf(size=15, angle=0):
    psf = np.zeros((size, size))
    psf[size//2, :] = 1.0 / size
    M = cv2.getRotationMatrix2D((size//2, size//2), angle, 1)
    psf = cv2.warpAffine(psf, M, (size, size))
    return psf / psf.sum()

@app.post("/api/module3/inverse_filter")
async def inverse_filter(
    file: UploadFile = File(...),
    blur_size: int = Form(10),
    angle: int = Form(0),
    noise_lvl: float = Form(5),
    threshold: float = Form(0.05)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    
    psf = motion_blur_psf(blur_size, angle)
    psf_pad = np.zeros_like(gray)
    ph, pw = psf.shape
    psf_pad[:ph, :pw] = psf
    
    H = np.fft.fft2(psf_pad)
    F = np.fft.fft2(gray)
    G = H * F
    if noise_lvl > 0:
        G += np.fft.fft2(np.random.normal(0, noise_lvl, gray.shape))
        
    degraded = np.abs(np.fft.ifft2(G))
    H_inv = np.where(np.abs(H) > threshold, 1.0/H, 0)
    restored = np.abs(np.fft.ifft2(np.fft.fft2(degraded) * H_inv))
    
    out_degraded = cv2.normalize(degraded, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    out_restored = cv2.normalize(restored, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Return both side-by-side
    combined = np.hstack((out_degraded, out_restored))
    return Response(content=encode_image(combined), media_type="image/jpeg")

@app.post("/api/module3/wiener_filter")
async def wiener_filter(
    file: UploadFile = File(...),
    blur_size: int = Form(10),
    angle: int = Form(0),
    noise_lvl: float = Form(10),
    K: float = Form(0.01)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    
    psf = motion_blur_psf(blur_size, angle)
    psf_pad = np.zeros_like(gray)
    ph, pw = psf.shape
    psf_pad[:ph, :pw] = psf
    
    H = np.fft.fft2(psf_pad)
    F = np.fft.fft2(gray)
    G = H * F
    if noise_lvl > 0:
        G += np.fft.fft2(np.random.normal(0, noise_lvl, gray.shape))
        
    degraded = np.real(np.fft.ifft2(G))
    H_conj = np.conj(H)
    H_w = H_conj / (np.abs(H)**2 + K)
    restored = np.real(np.fft.ifft2(H_w * np.fft.fft2(degraded)))
    
    out_degraded = cv2.normalize(degraded, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    out_restored = cv2.normalize(restored, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    combined = np.hstack((out_degraded, out_restored))
    return Response(content=encode_image(combined), media_type="image/jpeg")

@app.post("/api/module3/cls_filter")
async def cls_filter(
    file: UploadFile = File(...),
    blur_size: int = Form(8),
    noise_lvl: float = Form(15),
    gamma: float = Form(0.01)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    
    psf = motion_blur_psf(blur_size, 0)
    psf_pad = np.zeros_like(gray)
    psf_pad[:psf.shape[0], :psf.shape[1]] = psf
    
    H = np.fft.fft2(psf_pad)
    G = H * np.fft.fft2(gray)
    if noise_lvl > 0:
        G += np.fft.fft2(np.random.normal(0, noise_lvl, gray.shape))
    degraded = np.real(np.fft.ifft2(G))
    
    lap = np.array([[0,1,0],[1,-4,1],[0,1,0]], dtype=float)
    lap_pad = np.zeros_like(gray)
    lap_pad[:3, :3] = lap
    P = np.fft.fft2(lap_pad)
    
    H_conj = np.conj(H)
    H_cls = H_conj / (np.abs(H)**2 + gamma * np.abs(P)**2)
    restored = np.real(np.fft.ifft2(H_cls * np.fft.fft2(degraded)))
    
    out_degraded = cv2.normalize(degraded, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    out_restored = cv2.normalize(restored, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    combined = np.hstack((out_degraded, out_restored))
    return Response(content=encode_image(combined), media_type="image/jpeg")

# --- MODULE 4 ROUTES ---
import pywt

@app.post("/api/module4/color_models")
async def color_models(
    file: UploadFile = File(...),
    model: str = Form(...)
):
    img_rgb = read_imagefile(await file.read())
    
    if model == "RGB":
        c1, c2, c3 = img_rgb[:,:,0], img_rgb[:,:,1], img_rgb[:,:,2]
    elif model == "HSV":
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        c1, c2, c3 = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    elif model == "LAB":
        lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
        c1, c2, c3 = lab[:,:,0], lab[:,:,1], lab[:,:,2]
    elif model == "YCbCr":
        ycbcr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
        c1, c2, c3 = ycbcr[:,:,0], ycbcr[:,:,1], ycbcr[:,:,2]
    else: # CMY
        r, g, b = img_rgb[:,:,0]/255., img_rgb[:,:,1]/255., img_rgb[:,:,2]/255.
        c1, c2, c3 = ((1-r)*255).astype(np.uint8), ((1-g)*255).astype(np.uint8), ((1-b)*255).astype(np.uint8)
        
    # Resize them to fit nicely side by side to avoid huge payload
    h, w = img_rgb.shape[:2]
    max_h = 300
    if h > max_h:
        scale = max_h / h
        new_w = int(w * scale)
        img_rgb = cv2.resize(img_rgb, (new_w, max_h))
        c1 = cv2.resize(c1, (new_w, max_h))
        c2 = cv2.resize(c2, (new_w, max_h))
        c3 = cv2.resize(c3, (new_w, max_h))
        
    # Stack them: Original, C1, C2, C3
    c1_c = cv2.cvtColor(c1, cv2.COLOR_GRAY2RGB)
    c2_c = cv2.cvtColor(c2, cv2.COLOR_GRAY2RGB)
    c3_c = cv2.cvtColor(c3, cv2.COLOR_GRAY2RGB)
    
    combined = np.hstack((img_rgb, c1_c, c2_c, c3_c))
    return Response(content=encode_image(combined), media_type="image/jpeg")

@app.post("/api/module4/pseudo_color")
async def pseudo_color(
    file: UploadFile = File(...),
    mode: str = Form(...), # 'colormap' or 'slice'
    cmap: str = Form("Jet"),
    lo: int = Form(80),
    hi: int = Form(180)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    if mode == "colormap":
        cmaps = {
            "Jet": cv2.COLORMAP_JET, "Hot": cv2.COLORMAP_HOT, "Rainbow": cv2.COLORMAP_RAINBOW,
            "Ocean": cv2.COLORMAP_OCEAN, "HSV": cv2.COLORMAP_HSV, "Inferno": cv2.COLORMAP_INFERNO,
            "Turbo": cv2.COLORMAP_TURBO, "Viridis": cv2.COLORMAP_VIRIDIS
        }
        pseudo = cv2.applyColorMap(gray, cmaps.get(cmap, cv2.COLORMAP_JET))
        out = cv2.cvtColor(pseudo, cv2.COLOR_BGR2RGB)
    else:
        mask = (gray >= lo) & (gray <= hi)
        sliced = np.stack([gray]*3, axis=-1).copy()
        sliced[mask] = [255, 100, 0]
        sliced[~mask] = np.stack([gray[~mask]]*3, axis=-1)
        out = sliced
        
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module4/wavelets")
async def wavelets(
    file: UploadFile = File(...),
    wavelet: str = Form("haar"),
    level: int = Form(2),
    keep_pct: int = Form(10)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    
    coeffs = pywt.wavedec2(gray, wavelet, level=level)
    all_coeffs = np.concatenate([c.flatten() for arr in coeffs[1:] for c in arr])
    thresh = np.percentile(np.abs(all_coeffs), max(0, 100-keep_pct))
    
    coeffs_thresh = [coeffs[0]] + [
        tuple(np.where(np.abs(c) > thresh, c, 0) for c in level_coeffs)
        for level_coeffs in coeffs[1:]
    ]
    reconstructed = pywt.waverec2(coeffs_thresh, wavelet)
    out = cv2.normalize(reconstructed[:gray.shape[0], :gray.shape[1]], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module4/morphology")
async def morphology(
    file: UploadFile = File(...),
    op: str = Form(...),
    thresh_val: int = Form(127),
    se_shape: str = Form("Rectangle"),
    se_size: int = Form(5),
    iters: int = Form(1)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    
    shape_map = {"Rectangle": cv2.MORPH_RECT, "Ellipse": cv2.MORPH_ELLIPSE, "Cross": cv2.MORPH_CROSS}
    kernel = cv2.getStructuringElement(shape_map.get(se_shape, cv2.MORPH_RECT), (se_size, se_size))
    
    morph_map = {
        "Erosion": cv2.MORPH_ERODE, "Dilation": cv2.MORPH_DILATE, "Opening": cv2.MORPH_OPEN,
        "Closing": cv2.MORPH_CLOSE, "Gradient": cv2.MORPH_GRADIENT, "Top-Hat": cv2.MORPH_TOPHAT,
        "Black-Hat": cv2.MORPH_BLACKHAT
    }
    
    if op == "Skeletonisation":
        img_sk = binary.copy()
        skel = np.zeros_like(img_sk)
        kernel_sk = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
        for _ in range(100):
            eroded = cv2.erode(img_sk, kernel_sk)
            temp = cv2.dilate(eroded, kernel_sk)
            temp = cv2.subtract(img_sk, temp)
            skel = cv2.bitwise_or(skel, temp)
            img_sk = eroded.copy()
            if cv2.countNonZero(img_sk) == 0:
                break
        out = skel
    else:
        mtype = morph_map.get(op, cv2.MORPH_ERODE)
        if op in ["Erosion", "Dilation"]:
            out = cv2.morphologyEx(binary, mtype, kernel, iterations=iters)
        else:
            out = cv2.morphologyEx(binary, mtype, kernel)
            
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module4/hitormiss")
async def hitormiss(
    file: UploadFile = File(...),
    pattern: str = Form(...),
    thresh: int = Form(127)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
    
    if pattern == "isolated":
        b1 = np.array([[0,0,0],[0,1,0],[0,0,0]], dtype=np.int8)
        b2 = np.array([[1,1,1],[1,0,1],[1,1,1]], dtype=np.int8)
    elif pattern == "corner":
        b1 = np.array([[0,1,1],[0,1,1],[0,0,0]], dtype=np.int8)
        b2 = np.array([[1,0,0],[1,0,0],[1,1,1]], dtype=np.int8)
    else: # line end
        b1 = np.array([[0,0,0],[1,1,0],[0,0,0]], dtype=np.int8)
        b2 = np.array([[1,1,1],[0,0,1],[1,1,1]], dtype=np.int8)
        
    bin_norm = (binary // 255).astype(np.uint8)
    erode1 = cv2.erode(bin_norm, b1.clip(0,1))
    erode2 = cv2.erode(1 - bin_norm, b2.clip(0,1))
    out = cv2.bitwise_and(erode1, erode2) * 255
    
    return Response(content=encode_image(out), media_type="image/jpeg")

# --- MODULE 5 ROUTES ---
@app.post("/api/module5/edge_detection")
async def edge_detection(
    file: UploadFile = File(...),
    detector: str = Form(...),
    ksize: int = Form(3),
    sigma: float = Form(1.5),
    t1: int = Form(50),
    t2: int = Form(150),
    aperture: int = Form(3)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    if detector == "Sobel (X)":
        out = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=ksize))
    elif detector == "Sobel (Y)":
        out = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=ksize))
    elif detector == "Sobel (combined)":
        sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=ksize)
        sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=ksize)
        out = cv2.convertScaleAbs(np.sqrt(sx**2 + sy**2))
    elif detector == "Prewitt":
        kx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]], dtype=np.float32)
        ky = np.array([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=np.float32)
        px = cv2.filter2D(gray.astype(np.float32), -1, kx)
        py = cv2.filter2D(gray.astype(np.float32), -1, ky)
        out = cv2.convertScaleAbs(np.sqrt(px**2 + py**2))
    elif detector == "Roberts Cross":
        kr1 = np.array([[1,0],[0,-1]], dtype=np.float32)
        kr2 = np.array([[0,1],[-1,0]], dtype=np.float32)
        r1  = cv2.filter2D(gray.astype(np.float32), -1, kr1)
        r2  = cv2.filter2D(gray.astype(np.float32), -1, kr2)
        out = cv2.convertScaleAbs(np.sqrt(r1**2 + r2**2))
    elif detector == "Laplacian":
        out = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_32F, ksize=ksize))
    elif detector == "LoG":
        smoothed = cv2.GaussianBlur(gray, (ksize, ksize), sigma)
        out = cv2.convertScaleAbs(cv2.Laplacian(smoothed, cv2.CV_32F))
    else: # Canny
        out = cv2.Canny(gray, t1, t2, apertureSize=aperture)
        
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module5/hough")
async def hough_transforms(
    file: UploadFile = File(...),
    htype: str = Form(...),
    threshold: int = Form(80),
    min_len: int = Form(50),
    max_gap: int = Form(10),
    dp: float = Form(1.5),
    min_dist: int = Form(30),
    p1: int = Form(80),
    p2: int = Form(30),
    min_r: int = Form(10),
    max_r: int = Form(60)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    result = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    if htype == "line":
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold)
        if lines is not None:
            for line in lines[:50]:
                rho, theta = line[0]
                a, b = np.cos(theta), np.sin(theta)
                x0, y0 = a*rho, b*rho
                x1 = int(x0 + 1000*(-b)); y1 = int(y0 + 1000*a)
                x2 = int(x0 - 1000*(-b)); y2 = int(y0 - 1000*a)
                cv2.line(result, (x1,y1), (x2,y2), (255,100,0), 1)
                
    elif htype == "prob_line":
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold, minLineLength=min_len, maxLineGap=max_gap)
        if lines is not None:
            for line in lines:
                x1,y1,x2,y2 = line[0]
                cv2.line(result, (x1,y1), (x2,y2), (255,100,0), 2)
                
    else: # circles
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, min_dist, param1=p1, param2=p2, minRadius=min_r, maxRadius=max_r)
        if circles is not None:
            circles = np.round(circles[0,:]).astype(int)
            for (x,y,r) in circles:
                cv2.circle(result, (x,y), r, (0,200,255), 2)
                cv2.circle(result, (x,y), 2, (255,100,0), 3)
                
    return Response(content=encode_image(result), media_type="image/jpeg")

@app.post("/api/module5/thresholding")
async def thresholding(
    file: UploadFile = File(...),
    method: str = Form(...),
    T: int = Form(127),
    block: int = Form(11),
    C: int = Form(2),
    classes: int = Form(3)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    
    if method == "Manual":
        _, out = cv2.threshold(gray, T, 255, cv2.THRESH_BINARY)
    elif method == "Otsu":
        _, out = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == "Triangle":
        _, out = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
    elif method == "Adaptive Mean":
        out = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block, C)
    elif method == "Adaptive Gaussian":
        out = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, C)
    else: # Multi-level Otsu
        hist = cv2.calcHist([gray],[0],None,[256],[0,256]).flatten()
        thresholds = [0]
        remaining = gray.copy()
        for _ in range(classes-1):
            _, t = cv2.threshold(remaining, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            thresholds.append(int(t))
            remaining = np.where(remaining > t, remaining, 0).astype(np.uint8)
        ts = sorted(set(thresholds[1:]))
        out = np.zeros_like(gray)
        boundaries = [0] + ts + [255]
        for i in range(len(boundaries)-1):
            mask = (gray >= boundaries[i]) & (gray < boundaries[i+1])
            out[mask] = int(255 * i / (len(boundaries)-2))
            
    return Response(content=encode_image(out), media_type="image/jpeg")

@app.post("/api/module5/corners")
async def corners(
    file: UploadFile = File(...),
    detector: str = Form(...),
    block: int = Form(2),
    ksize: int = Form(3),
    k: float = Form(0.04),
    thresh: int = Form(10),
    max_corners: int = Form(100),
    quality: float = Form(0.01),
    min_dist: int = Form(10),
    fast_thresh: int = Form(10),
    use_nms: bool = Form(True)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    if detector == "Harris":
        dst = cv2.cornerHarris(gray, block, ksize, k)
        dst = cv2.dilate(dst, None)
        T_val = (thresh/100.0) * dst.max()
        overlay[dst > T_val] = [255, 0, 0]
    elif detector == "Shi-Tomasi":
        c_pts = cv2.goodFeaturesToTrack(gray, max_corners, quality, min_dist)
        if c_pts is not None:
            c_pts = np.int0(c_pts)
            for c in c_pts:
                x,y = c.ravel()
                cv2.circle(overlay, (x,y), 4, (255,100,0), -1)
    else: # FAST
        fast = cv2.FastFeatureDetector_create(threshold=fast_thresh, nonmaxSuppression=use_nms)
        kps = fast.detect(gray)
        for kp in kps:
            x, y = int(kp.pt[0]), int(kp.pt[1])
            cv2.circle(overlay, (x,y), 3, (0,255,100), -1)
            
    return Response(content=encode_image(overlay), media_type="image/jpeg")

@app.post("/api/module5/descriptors")
async def descriptors(
    file: UploadFile = File(...),
    thresh: int = Form(127),
    num_show: int = Form(5)
):
    img = read_imagefile(await file.read())
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(overlay, contours, -1, (255,100,0), 2)
    
    results = []
    if contours:
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:num_show]
        for cnt in contours_sorted:
            area = cv2.contourArea(cnt)
            perim = cv2.arcLength(cnt, True)
            M = cv2.moments(cnt)
            circularity = (4*np.pi*area / (perim**2)) if perim > 0 else 0
            cx = M["m10"]/M["m00"] if M["m00"] > 0 else 0
            cy = M["m01"]/M["m00"] if M["m00"] > 0 else 0
            hu = cv2.HuMoments(M).flatten().tolist()
            x,y,w,h = cv2.boundingRect(cnt)
            aspect = w/h if h > 0 else 0
            
            results.append({
                "area": area,
                "perimeter": perim,
                "circularity": circularity,
                "cx": cx,
                "cy": cy,
                "aspect": aspect,
                "hu": hu
            })
            
    img_bytes = encode_image(overlay)
    import base64
    b64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return JSONResponse(content={"image": f"data:image/jpeg;base64,{b64}", "data": results})

# --- TOOLS ROUTES ---

@app.post("/api/tools/gallery")
async def tool_gallery_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/comparison")
async def tool_comparison_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/superresolution")
async def tool_superresolution_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/labreport")
async def tool_labreport_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/quiz")
async def tool_quiz_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/webcam")
async def tool_webcam_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/jpegcompression")
async def tool_jpegcompression_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/gifanimator")
async def tool_gifanimator_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/batchprocessing")
async def tool_batchprocessing_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/codeexporter")
async def tool_codeexporter_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/parameterchallenge")
async def tool_parameterchallenge_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/featuredescriptors")
async def tool_featuredescriptors_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/opticalflow")
async def tool_opticalflow_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/sessionrecorder")
async def tool_sessionrecorder_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/qualitymetrics")
async def tool_qualitymetrics_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/templatematching")
async def tool_templatematching_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/documentscanner")
async def tool_documentscanner_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/forgerydetector")
async def tool_forgerydetector_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

@app.post("/api/tools/imagestitching")
async def tool_imagestitching_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")

# -- Serve React Frontend -------------------------------------------------------
# Mount the built React files from the 'static' directory
static_path = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_path):
    app.mount('/', StaticFiles(directory=static_path, html=True), name='static')

    # Catch-all route for React Router (SPA)
    @app.get('/{full_path:path}')
    async def serve_react_app(full_path: str):
        # Prevent intercepting /api or /health
        if (full_path.startswith('api') or 
            full_path.startswith('health') or 
            full_path.startswith('docs') or 
            full_path.startswith('openapi.json')):
            raise HTTPException(status_code=404)
        return FileResponse(os.path.join(static_path, 'index.html'))
