import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { lazy, Suspense } from 'react'
import Navbar from './components/Navbar'

// Lazy-load pages for faster initial load
const Login           = lazy(() => import('./pages/Login'))
const Home            = lazy(() => import('./pages/Home'))
const Modules         = lazy(() => import('./pages/Modules'))
const Tools           = lazy(() => import('./pages/Tools'))
const StreamlitViewer = lazy(() => import('./pages/StreamlitViewer'))
const Module1Fundamentals = lazy(() => import('./pages/Module1Fundamentals'))
const Module2SpatialFrequency = lazy(() => import('./pages/Module2SpatialFrequency'))
const Module3Restoration = lazy(() => import('./pages/Module3Restoration'))
const Module4ColorMorphology = lazy(() => import('./pages/Module4ColorMorphology'))
const Module5Segmentation = lazy(() => import('./pages/Module5Segmentation'))
const CinematicTitle = lazy(() => import('./pages/CinematicTitle'))

const ToolComparison = lazy(() => import('./pages/tools/ToolComparison'))
const ToolSuperResolution = lazy(() => import('./pages/tools/ToolSuperResolution'))
const ToolLabReport = lazy(() => import('./pages/tools/ToolLabReport'))
const ToolQuiz = lazy(() => import('./pages/tools/ToolQuiz'))
const ToolWebcam = lazy(() => import('./pages/tools/ToolWebcam'))
const ToolJPEGCompression = lazy(() => import('./pages/tools/ToolJPEGCompression'))
const ToolGIFAnimator = lazy(() => import('./pages/tools/ToolGIFAnimator'))
const ToolBatchProcessing = lazy(() => import('./pages/tools/ToolBatchProcessing'))
const ToolCodeExporter = lazy(() => import('./pages/tools/ToolCodeExporter'))
const ToolCodeExplainer = lazy(() => import('./pages/tools/ToolCodeExplainer'))
const ToolParameterChallenge = lazy(() => import('./pages/tools/ToolParameterChallenge'))
const ToolFeatureDescriptors = lazy(() => import('./pages/tools/ToolFeatureDescriptors'))
const ToolOpticalFlow = lazy(() => import('./pages/tools/ToolOpticalFlow'))
const ToolSessionRecorder = lazy(() => import('./pages/tools/ToolSessionRecorder'))
const ToolQualityMetrics = lazy(() => import('./pages/tools/ToolQualityMetrics'))
const ToolTemplateMatching = lazy(() => import('./pages/tools/ToolTemplateMatching'))
const ToolDocumentScanner = lazy(() => import('./pages/tools/ToolDocumentScanner'))
const ToolForgeryDetector = lazy(() => import('./pages/tools/ToolForgeryDetector'))
const ToolImageStitching = lazy(() => import('./pages/tools/ToolImageStitching'))

const PageLoader = () => (
  <div style={{
    minHeight: '100vh', background: '#0d1117',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexDirection: 'column', gap: '16px',
  }}>
    <div style={{ fontSize: '2.5rem', animation: 'spin 1.2s linear infinite' }}>🔬</div>
    <div style={{ color: 'rgba(230,237,243,0.4)', fontSize: '0.8rem', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
      Loading…
    </div>
    <style>{`@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }`}</style>
  </div>
)

function ProtectedRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const { user } = useAuth()

  return (
    <ThemeProvider>
      {user && <Navbar />}
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/login"   element={user ? <Navigate to="/" replace /> : <Login />} />
          <Route path="/"          element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/title"     element={<CinematicTitle />} />
          <Route path="/modules"   element={<ProtectedRoute><Modules /></ProtectedRoute>} />
          <Route path="/tools"     element={<ProtectedRoute><Tools /></ProtectedRoute>} />
          <Route path="/simulator" element={<ProtectedRoute><StreamlitViewer /></ProtectedRoute>} />
          <Route path="/module1"   element={<ProtectedRoute><Module1Fundamentals /></ProtectedRoute>} />
          <Route path="/module2"   element={<ProtectedRoute><Module2SpatialFrequency /></ProtectedRoute>} />
          <Route path="/module3"   element={<ProtectedRoute><Module3Restoration /></ProtectedRoute>} />
          <Route path="/module4"   element={<ProtectedRoute><Module4ColorMorphology /></ProtectedRoute>} />
          <Route path="/module5"   element={<ProtectedRoute><Module5Segmentation /></ProtectedRoute>} />
          <Route path="/tool/comparison" element={<ProtectedRoute><ToolComparison /></ProtectedRoute>} />
          <Route path="/tool/superresolution" element={<ProtectedRoute><ToolSuperResolution /></ProtectedRoute>} />
          <Route path="/tool/labreport" element={<ProtectedRoute><ToolLabReport /></ProtectedRoute>} />
          <Route path="/tool/quiz" element={<ProtectedRoute><ToolQuiz /></ProtectedRoute>} />
          <Route path="/tool/webcam" element={<ProtectedRoute><ToolWebcam /></ProtectedRoute>} />
          <Route path="/tool/jpegcompression" element={<ProtectedRoute><ToolJPEGCompression /></ProtectedRoute>} />
          <Route path="/tool/gifanimator" element={<ProtectedRoute><ToolGIFAnimator /></ProtectedRoute>} />
          <Route path="/tool/batchprocessing" element={<ProtectedRoute><ToolBatchProcessing /></ProtectedRoute>} />
          <Route path="/tool/codeexporter" element={<ProtectedRoute><ToolCodeExporter /></ProtectedRoute>} />
          <Route path="/tool/codeexplainer" element={<ProtectedRoute><ToolCodeExplainer /></ProtectedRoute>} />
          <Route path="/tool/parameterchallenge" element={<ProtectedRoute><ToolParameterChallenge /></ProtectedRoute>} />
          <Route path="/tool/featuredescriptors" element={<ProtectedRoute><ToolFeatureDescriptors /></ProtectedRoute>} />
          <Route path="/tool/opticalflow" element={<ProtectedRoute><ToolOpticalFlow /></ProtectedRoute>} />
          <Route path="/tool/sessionrecorder" element={<ProtectedRoute><ToolSessionRecorder /></ProtectedRoute>} />
          <Route path="/tool/qualitymetrics" element={<ProtectedRoute><ToolQualityMetrics /></ProtectedRoute>} />
          <Route path="/tool/templatematching" element={<ProtectedRoute><ToolTemplateMatching /></ProtectedRoute>} />
          <Route path="/tool/documentscanner" element={<ProtectedRoute><ToolDocumentScanner /></ProtectedRoute>} />
          <Route path="/tool/forgerydetector" element={<ProtectedRoute><ToolForgeryDetector /></ProtectedRoute>} />
          <Route path="/tool/imagestitching" element={<ProtectedRoute><ToolImageStitching /></ProtectedRoute>} />
          <Route path="*"          element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </ThemeProvider>
  )
}
