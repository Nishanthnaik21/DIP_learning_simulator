
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
