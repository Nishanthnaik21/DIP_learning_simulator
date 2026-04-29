import os
import re

tools = [
    ("6_Gallery.py", "Gallery", "🖼️"),
    ("7_Comparison.py", "Comparison", "⚖️"),
    ("8_SuperResolution.py", "SuperResolution", "🔍"),
    ("9_LabReport.py", "LabReport", "📝"),
    ("10_Quiz.py", "Quiz", "❓"),
    ("11_Webcam.py", "Webcam", "📷"),
    ("12_JPEG_Compression.py", "JPEGCompression", "🗜️"),
    ("13_GIF_Animator.py", "GIFAnimator", "🎞️"),
    ("14_Batch_Processing.py", "BatchProcessing", "📦"),
    ("15_Code_Exporter.py", "CodeExporter", "💻"),
    ("16_Parameter_Challenge.py", "ParameterChallenge", "🎯"),
    ("17_Feature_Descriptors.py", "FeatureDescriptors", "✨"),
    ("18_Optical_Flow.py", "OpticalFlow", "🌊"),
    ("19_Session_Recorder.py", "SessionRecorder", "⏺️"),
    ("20_Quality_Metrics.py", "QualityMetrics", "📊"),
    ("21_Template_Matching.py", "TemplateMatching", "🧩"),
    ("22_Document_Scanner.py", "DocumentScanner", "📄"),
    ("23_Forgery_Detector.py", "ForgeryDetector", "🕵️"),
    ("24_Image_Stitching.py", "ImageStitching", "panorama")
]

react_template = """import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function Tool{name}() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [resultImage, setResultImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0]
      setFile(selected)
      setPreviewUrl(URL.createObjectURL(selected))
      setResultImage(null)
    }
  }

  const runTool = async () => {
    if (!file) return
    setLoading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const res = await axios.post(`/api/tools/{endpoint}`, fd, { responseType: 'blob' })
      setResultImage(URL.createObjectURL(res.data))
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>
            ← Back
          </button>
          <span style={{ fontSize: '2rem' }}>{icon}</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>Tool: {name}</h1>
        </div>

        <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', marginBottom: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontFamily: 'var(--font-heading)' }}>Upload Image</h3>
          <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <button onClick={() => fileInputRef.current.click()} style={{ background: 'var(--blue)', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: 600 }}>
              Choose File
            </button>
            {previewUrl && <img src={previewUrl} alt="Preview" style={{ height: '80px', borderRadius: '8px', border: '1px solid var(--border)' }} />}
          </div>
        </div>

        {file && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '24px', borderRadius: '16px', minHeight: '400px' }}>
            <div style={{ display: 'flex', gap: '16px', marginBottom: '20px' }}>
               <button onClick={runTool} disabled={loading} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>
                 {loading ? 'Processing...' : 'Run Tool'}
               </button>
            </div>
            
            <div style={{ display: 'flex', gap: '20px' }}>
              <div style={{ flex: 1 }}>
                <h4 style={{ textAlign: 'center', marginTop: 0 }}>Input</h4>
                <img src={previewUrl} alt="Original" style={{ width: '100%', borderRadius: '8px' }} />
              </div>
              <div style={{ flex: 1 }}>
                <h4 style={{ textAlign: 'center', marginTop: 0 }}>Output</h4>
                {resultImage && <img src={resultImage} alt="Processed" style={{ width: '100%', borderRadius: '8px' }} />}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
"""

fastapi_route_template = """
@app.post("/api/tools/{endpoint}")
async def tool_{endpoint}_api(file: UploadFile = File(...)):
    img = read_imagefile(await file.read())
    # Generic placeholder: just return grayscale for now to prove it works
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return Response(content=encode_image(gray), media_type="image/jpeg")
"""

os.makedirs('frontend/src/pages/tools', exist_ok=True)

# Generate React files
for filename, name, icon in tools:
    endpoint = name.lower()
    content = react_template.replace('{name}', name).replace('{icon}', icon).replace('{endpoint}', endpoint)
    with open(f'frontend/src/pages/tools/Tool{name}.jsx', 'w', encoding='utf-8') as f:
        f.write(content)

# Generate FastAPI endpoints file
backend_routes = ""
for filename, name, icon in tools:
    endpoint = name.lower()
    backend_routes += fastapi_route_template.format(endpoint=endpoint)

with open('backend/tools_append.py', 'w', encoding='utf-8') as f:
    f.write(backend_routes)

# Update App.jsx
app_jsx_path = 'frontend/src/App.jsx'
with open(app_jsx_path, 'r', encoding='utf-8') as f:
    app_jsx = f.read()

imports = ""
routes = ""
for filename, name, icon in tools:
    imports += f"const Tool{name} = lazy(() => import('./pages/tools/Tool{name}'))\n"
    routes += f'          <Route path="/tool/{name.lower()}" element={{<ProtectedRoute><Tool{name} /></ProtectedRoute>}} />\n'

if "const ToolGallery" not in app_jsx:
    # insert imports before "const PageLoader"
    app_jsx = app_jsx.replace("const PageLoader = () => (", imports + "\nconst PageLoader = () => (")
    # insert routes before "<Route path=\"*\""
    app_jsx = app_jsx.replace('<Route path="*"          element={<Navigate to="/" replace />} />', routes + '          <Route path="*"          element={<Navigate to="/" replace />} />')
    with open(app_jsx_path, 'w', encoding='utf-8') as f:
        f.write(app_jsx)

# Update api.js
api_js_path = 'frontend/src/utils/api.js'
with open(api_js_path, 'r', encoding='utf-8') as f:
    api_js = f.read()

tool_routing = ""
for filename, name, icon in tools:
    tool_routing += f"  }} else if (streamlitPage && streamlitPage.includes('{filename.split('.')[0]}')) {{\n    navigate('/tool/{name.lower()}')\n"

if "/tool/gallery" not in api_js:
    # insert into openTool
    new_openTool = """export function openTool(navigate, streamlitPage) {
""" + tool_routing[6:] + """  } else {
    navigate(simulatorPath(streamlitPage, 'Tool', '/'))
  }
}"""
    api_js = re.sub(r"export function openTool\(navigate, page\) \{.*?\n\}", new_openTool, api_js, flags=re.DOTALL)
    with open(api_js_path, 'w', encoding='utf-8') as f:
        f.write(api_js)

print("Generation complete!")
