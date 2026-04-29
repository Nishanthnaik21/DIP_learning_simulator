
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
