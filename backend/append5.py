
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
