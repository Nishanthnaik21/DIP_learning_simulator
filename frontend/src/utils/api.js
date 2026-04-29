import axios from 'axios'

// With Vite's proxy config, /api calls are forwarded to FastAPI on port 8000
const http = axios.create({ baseURL: '/', timeout: 12000 })

// Base URL for the Streamlit app
export const STREAMLIT_BASE = 'http://localhost:8501'

// ─── Navigation helpers ────────────────────────────────────────────────────────
/**
 * Build a /simulator URL for react-router navigation.
 * Usage: navigate(simulatorPath(page, label, from))
 */
export function simulatorPath(streamlitPage, label = 'Simulator', from = '/') {
  const params = new URLSearchParams({ label, from })
  if (streamlitPage) params.set('page', streamlitPage)
  return `/simulator?${params.toString()}`
}

/** Open the Streamlit app homepage INSIDE the React viewer */
export function openStreamlit(navigate, from = '/') {
  navigate(simulatorPath('', 'DIP Simulator', from))
}

/** Open a specific module inside the React viewer */
export function openModule(navigate, streamlitPage) {
  const toolName = streamlitPage?.split('_')?.[1] || 'Module';
  dataAPI.recordActivity(toolName).catch(() => {});

  if (streamlitPage && streamlitPage.includes('Module1')) {
    navigate('/module1')
  } else if (streamlitPage && streamlitPage.includes('Module2')) {
    navigate('/module2')
  } else if (streamlitPage && streamlitPage.includes('Module3')) {
    navigate('/module3')
  } else if (streamlitPage && streamlitPage.includes('Module4')) {
    navigate('/module4')
  } else if (streamlitPage && streamlitPage.includes('Module5')) {
    navigate('/module5')
  } else {
    navigate(simulatorPath(streamlitPage, 'Module', '/'))
  }
}

/** Open a specific tool inside the React viewer */
export function openTool(navigate, streamlitPage) {
  const toolName = streamlitPage?.split('_')?.[1] || 'Tool';
  dataAPI.recordActivity(toolName).catch(() => {});

  if (streamlitPage && streamlitPage.includes('7_Comparison')) {
    navigate('/tool/comparison')
  } else if (streamlitPage && streamlitPage.includes('8_SuperResolution')) {
    navigate('/tool/superresolution')
  } else if (streamlitPage && streamlitPage.includes('9_LabReport')) {
    navigate('/tool/labreport')
  } else if (streamlitPage && streamlitPage.includes('10_Quiz')) {
    navigate('/tool/quiz')
  } else if (streamlitPage && streamlitPage.includes('11_Webcam')) {
    navigate('/tool/webcam')
  } else if (streamlitPage && streamlitPage.includes('12_JPEG_Compression')) {
    navigate('/tool/jpegcompression')
  } else if (streamlitPage && streamlitPage.includes('13_GIF_Animator')) {
    navigate('/tool/gifanimator')
  } else if (streamlitPage && streamlitPage.includes('14_Batch_Processing')) {
    navigate('/tool/batchprocessing')
  } else if (streamlitPage && streamlitPage.includes('15_Code_Exporter')) {
    navigate('/tool/codeexporter')
  } else if (streamlitPage && streamlitPage.includes('15_Code_Explainer')) {
    navigate('/tool/codeexplainer')
  } else if (streamlitPage && streamlitPage.includes('16_Parameter_Challenge')) {
    navigate('/tool/parameterchallenge')
  } else if (streamlitPage && streamlitPage.includes('17_Feature_Descriptors')) {
    navigate('/tool/featuredescriptors')
  } else if (streamlitPage && streamlitPage.includes('18_Optical_Flow')) {
    navigate('/tool/opticalflow')
  } else if (streamlitPage && streamlitPage.includes('19_Session_Recorder')) {
    navigate('/tool/sessionrecorder')
  } else if (streamlitPage && streamlitPage.includes('20_Quality_Metrics')) {
    navigate('/tool/qualitymetrics')
  } else if (streamlitPage && streamlitPage.includes('21_Template_Matching')) {
    navigate('/tool/templatematching')
  } else if (streamlitPage && streamlitPage.includes('22_Document_Scanner')) {
    navigate('/tool/documentscanner')
  } else if (streamlitPage && streamlitPage.includes('23_Forgery_Detector')) {
    navigate('/tool/forgerydetector')
  } else if (streamlitPage && streamlitPage.includes('24_Image_Stitching')) {
    navigate('/tool/imagestitching')
  } else {
    navigate(simulatorPath(streamlitPage, 'Tool', '/'))
  }
}

// ─── Auth API ─────────────────────────────────────────────────────────────────
export const authAPI = {
  login:    (email, password) =>
    http.post('/api/auth/login', { email, password }),
  register: (email, password, username = '', role = 'student') =>
    http.post('/api/auth/register', { email, password, username, role }),
}

// ─── Data API ─────────────────────────────────────────────────────────────────
export const dataAPI = {
  modules: () => http.get('/api/modules'),
  tools:   () => http.get('/api/tools'),
  stats:   () => http.get('/api/stats'),
  recordActivity: (tool) => {
    const fd = new FormData();
    fd.append('tool', tool);
    return http.post('/api/stats/record', fd);
  },
  health:  () => http.get('/health'),
}
