
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
