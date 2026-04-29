"""utils/api.py — FastAPI REST API for DIP Learning Simulator v4.

Run from the dip_simulator/ directory:
    python -m uvicorn utils.api:app --reload --port 8000
"""
from __future__ import annotations
import sys, os

# Ensure dip_simulator/ is on path so 'utils.db' resolves correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ─── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DIP Learning Simulator API",
    description="REST API powering the 3D React/Three.js frontend — DIP Simulator v4",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Try to connect to MySQL DB once at startup ───────────────────────────────
DB_OK = False
_db_authenticate = None
_db_register_user = None

try:
    from utils.db import authenticate as _auth, register_user as _reg, check_connection, init_db
    ok, _ = check_connection()
    if ok:
        init_db()
        _db_authenticate = _auth
        _db_register_user = _reg
        DB_OK = True
except Exception:
    pass  # Will use fallback credentials

# ─── Fallback credentials (used when DB is offline) ───────────────────────────
FALLBACK_USERS = {
    "admin":   {"password": "dip2024",  "role": "admin",   "email": "admin@dip.edu"},
    "student": {"password": "learn123", "role": "student", "email": "student@dip.edu"},
    "guest":   {"password": "guest",    "role": "guest",   "email": "guest@dip.edu"},
}

# ─── Pydantic request models ───────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = ""
    role: Optional[str] = "student"

# ─── Auth endpoints ────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """Authenticate user via MySQL DB or fallback credentials."""
    user = None

    # 1. Try DB authentication (using email)
    if DB_OK and _db_authenticate:
        try:
            user = _db_authenticate(req.email, req.password)
        except Exception:
            pass

    # 2. Fallback to hardcoded demo users (match by email)
    if user is None:
        email = req.email.strip().lower()
        for uname, fb in FALLBACK_USERS.items():
            if fb["email"].lower() == email and fb["password"] == req.password:
                user = {"username": uname, "role": fb["role"], "email": fb["email"]}
                break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "username": user.get("username", "user"),
        "role":     user.get("role", "student"),
        "email":    user.get("email", ""),
        "db_auth":  DB_OK,
        "message":  "Authenticated successfully",
    }


@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    """Register a new user (requires MySQL connection)."""
    if not DB_OK or _db_register_user is None:
        raise HTTPException(
            status_code=503,
            detail="Registration requires a MySQL database connection. Configure Railway MySQL to enable."
        )
    ok, msg = _db_register_user(
        req.email, req.password,
        req.username or req.email.split('@')[0], req.role or "student"
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg, "username": req.username}


# ─── Module metadata ──────────────────────────────────────────────────────────
MODULES = [
    {
        "id": 1, "number": "01", "icon": "🖼️",
        "title": "Image Fundamentals",
        "subtitle": "Pixels, Sampling & Quantization",
        "description": "Explore the building blocks of digital images — pixels, sampling, quantization, colour channels and image statistics.",
        "topics": ["Pixel Inspector", "Sampling", "Quantization", "Channels", "Statistics"],
        "color": "#4361ee",
        "streamlit_page": "Module1_Fundamentals",
    },
    {
        "id": 2, "number": "02", "icon": "📡",
        "title": "Spatial & Frequency",
        "subtitle": "Filtering & Transforms",
        "description": "Master spatial domain filtering and frequency domain processing including DFT, histogram equalisation, and filter design.",
        "topics": ["Histogram EQ", "CLAHE", "Smoothing", "Sharpening", "DFT", "Freq Filters"],
        "color": "#b44fff",
        "streamlit_page": "Module2_SpatialFrequency",
    },
    {
        "id": 3, "number": "03", "icon": "🔧",
        "title": "Image Restoration",
        "subtitle": "Noise Removal & Deblurring",
        "description": "Restore degraded images using inverse filtering, Wiener filtering, CLS filtering. Evaluate quality with PSNR/SSIM.",
        "topics": ["Noise Models", "Inverse Filter", "Wiener", "CLS Filter", "PSNR/SSIM"],
        "color": "#4cc9f0",
        "streamlit_page": "Module3_Restoration",
    },
    {
        "id": 4, "number": "04", "icon": "🎨",
        "title": "Color & Morphology",
        "subtitle": "Color Models & Shape Analysis",
        "description": "Explore colour spaces, pseudo-colouring, wavelets and morphological operations for shape analysis.",
        "topics": ["Color Models", "Pseudo-Color", "Wavelets", "Morph Ops", "Hit-or-Miss"],
        "color": "#f8961e",
        "streamlit_page": "Module4_ColorMorphology",
    },
    {
        "id": 5, "number": "05", "icon": "✂️",
        "title": "Image Segmentation",
        "subtitle": "Object Detection & Analysis",
        "description": "Segment images and detect objects using edge detection, Hough transforms, thresholding, corners and feature descriptors.",
        "topics": ["Edge Detection", "Hough Transform", "Thresholding", "Corners", "Descriptors"],
        "color": "#ff3366",
        "streamlit_page": "Module5_Segmentation",
    },
]

# ─── Tool metadata ────────────────────────────────────────────────────────────
TOOLS = [
    {"id":  1, "icon": "🖼️", "name": "Sample Gallery",      "desc": "10 classic DIP images",       "color": "#4361ee", "page": "Gallery"},
    {"id":  2, "icon": "↔️", "name": "Compare Slider",      "desc": "Drag to compare before/after", "color": "#4cc9f0", "page": "Comparison"},
    {"id":  3, "icon": "🔭", "name": "Super Resolution",    "desc": "6 upscaling methods",          "color": "#b44fff", "page": "SuperResolution"},
    {"id":  4, "icon": "📄", "name": "PDF Lab Report",      "desc": "Auto-generate lab record",     "color": "#f8961e", "page": "LabReport"},
    {"id":  5, "icon": "🧠", "name": "Quiz Mode",           "desc": "25 MCQs + instant scoring",    "color": "#ff3366", "page": "Quiz"},
    {"id":  6, "icon": "📷", "name": "Webcam Capture",      "desc": "Live camera DIP effects",      "color": "#4361ee", "page": "Webcam"},
    {"id":  7, "icon": "🗜️", "name": "JPEG Compression",   "desc": "DCT block simulator",          "color": "#4cc9f0", "page": "JPEG_Compression"},
    {"id":  8, "icon": "✨", "name": "GIF Animator",        "desc": "Parameter sweep GIF",          "color": "#b44fff", "page": "GIF_Animator"},
    {"id":  9, "icon": "📦", "name": "Batch Processing",    "desc": "Multi-image pipeline",         "color": "#f8961e", "page": "Batch_Processing"},
    {"id": 10, "icon": "💻", "name": "Code Exporter",       "desc": "Export Python code",           "color": "#ff3366", "page": "Code_Exporter"},
    {"id": 11, "icon": "🎯", "name": "Param Challenge",     "desc": "Match the target image",       "color": "#4361ee", "page": "Parameter_Challenge"},
    {"id": 12, "icon": "📐", "name": "Feature Descriptors", "desc": "SIFT, HOG, ORB",               "color": "#4cc9f0", "page": "Feature_Descriptors"},
    {"id": 13, "icon": "🌊", "name": "Optical Flow",        "desc": "Motion estimation",            "color": "#b44fff", "page": "Optical_Flow"},
    {"id": 14, "icon": "📊", "name": "Session Recorder",    "desc": "Save & export session",        "color": "#f8961e", "page": "Session_Recorder"},
    {"id": 15, "icon": "📏", "name": "Quality Metrics",     "desc": "PSNR SSIM MSE VIF",            "color": "#ff3366", "page": "Quality_Metrics"},
    {"id": 16, "icon": "🔍", "name": "Template Matching",   "desc": "Cross-correlation",            "color": "#4361ee", "page": "Template_Matching"},
    {"id": 17, "icon": "📋", "name": "Doc Scanner",         "desc": "Perspective + OCR",            "color": "#4cc9f0", "page": "Document_Scanner"},
    {"id": 18, "icon": "🕵️", "name": "Forgery Detector",   "desc": "ELA tampering check",          "color": "#b44fff", "page": "Forgery_Detector"},
    {"id": 19, "icon": "🔗", "name": "Image Stitching",     "desc": "Panorama builder",             "color": "#f8961e", "page": "Image_Stitching"},
]

# ─── Data endpoints ───────────────────────────────────────────────────────────
@app.get("/api/modules")
async def get_modules():
    return {"modules": MODULES, "total": len(MODULES)}


@app.get("/api/tools")
async def get_tools():
    return {"tools": TOOLS, "total": len(TOOLS)}


@app.get("/api/stats")
async def get_stats():
    return {
        "modules":      5,
        "tools":        19,
        "pages":        24,
        "version":      "4.0",
        "course":       "22AIM61",
        "db_connected": DB_OK,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "db_connected": DB_OK, "api_version": "1.0.0"}
