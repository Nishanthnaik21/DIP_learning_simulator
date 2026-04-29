
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
