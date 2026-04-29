import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

const QUESTIONS = [
  { q: "What does DIP stand for?", opts: ["Digital Image Processing","Direct Image Projection","Dynamic Image Pipeline","Discrete Image Protocol"], ans: 0 },
  { q: "Which color model uses Hue, Saturation, Value?", opts: ["RGB","CMYK","HSV","YCbCr"], ans: 2 },
  { q: "What is the range of pixel values in an 8-bit grayscale image?", opts: ["0–255","1–256","0–127","0–1023"], ans: 0 },
  { q: "Histogram equalization is used to:", opts: ["Add noise","Improve contrast","Blur the image","Detect edges"], ans: 1 },
  { q: "Which filter is best for removing salt-and-pepper noise?", opts: ["Gaussian","Mean","Median","Laplacian"], ans: 2 },
  { q: "The Fourier Transform converts an image from:", opts: ["Spatial to frequency domain","RGB to grayscale","Time to spatial domain","Frequency to color domain"], ans: 0 },
  { q: "What does the Laplacian operator detect?", opts: ["Color changes","Edges (second derivative)","Texture","Noise"], ans: 1 },
  { q: "CLAHE stands for:", opts: ["Contrast Limited Adaptive Histogram Equalization","Color Linear Adaptive Histogram Enhancement","Cumulative Laplacian Adaptive Histogram Equalization","Contrast Linearized Adaptive Histogram Expansion"], ans: 0 },
  { q: "Which morphological operation shrinks binary objects?", opts: ["Dilation","Erosion","Opening","Closing"], ans: 1 },
  { q: "Sobel operator computes:", opts: ["Second derivative","First derivative / gradient","Histogram","DCT coefficients"], ans: 1 },
  { q: "JPEG compression uses which transform?", opts: ["DFT","DWT","DCT","DIT"], ans: 2 },
  { q: "How many bits per pixel in a true-color RGB image?", opts: ["8","16","24","32"], ans: 2 },
  { q: "Which domain does Wiener filter operate in?", opts: ["Spatial","Frequency","Color","Wavelet"], ans: 1 },
  { q: "Opening = Erosion followed by:", opts: ["Dilation","Erosion","Closing","Thresholding"], ans: 0 },
  { q: "Otsu's method is used for:", opts: ["Edge detection","Noise removal","Automatic thresholding","Color segmentation"], ans: 2 },
  { q: "The Canny edge detector uses:", opts: ["Only Sobel","Gaussian + gradient + NMS + hysteresis","Laplacian alone","Fourier transform"], ans: 1 },
  { q: "What is the Y channel in YCbCr?", opts: ["Blue chrominance","Red chrominance","Luma (brightness)","Hue"], ans: 2 },
  { q: "Wavelet transform provides:", opts: ["Only frequency info","Only spatial info","Both spatial and frequency info","Neither"], ans: 2 },
  { q: "Harris corner detector responds to:", opts: ["Edges only","Flat regions","Corners","Noise"], ans: 2 },
  { q: "Pseudo-coloring converts:", opts: ["Color to grayscale","Grayscale to color for visualization","RGB to HSV","BGR to RGB"], ans: 1 },
]

const TOTAL_TIME = 600 // 10 minutes

export default function ToolQuiz() {
  const navigate = useNavigate()
  const [phase, setPhase] = useState('intro') // intro | quiz | review
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState(Array(QUESTIONS.length).fill(null))
  const [timeLeft, setTimeLeft] = useState(TOTAL_TIME)
  const [selected, setSelected] = useState(null)
  const timerRef = useRef(null)

  const score = answers.reduce((acc, a, i) => acc + (a === QUESTIONS[i].ans ? 1 : 0), 0)

  useEffect(() => {
    if (phase === 'quiz') {
      timerRef.current = setInterval(() => {
        setTimeLeft(t => {
          if (t <= 1) { clearInterval(timerRef.current); setPhase('review'); return 0 }
          return t - 1
        })
      }, 1000)
    }
    return () => clearInterval(timerRef.current)
  }, [phase])

  const selectOpt = (idx) => setSelected(idx)

  const next = () => {
    if (selected === null) return
    const newAns = [...answers]; newAns[current] = selected
    setAnswers(newAns)
    setSelected(null)
    if (current + 1 >= QUESTIONS.length) { clearInterval(timerRef.current); setPhase('review') }
    else setCurrent(current + 1)
  }

  const mm = String(Math.floor(timeLeft / 60)).padStart(2, '0')
  const ss = String(timeLeft % 60).padStart(2, '0')
  const pct = Math.round((score / QUESTIONS.length) * 100)

  const cardStyle = { background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '28px', borderRadius: '16px' }

  return (
    <div className="with-navbar" style={{ minHeight: '100vh', padding: '40px 32px 80px', background: 'var(--bg)', color: 'var(--text)' }}>
      <div style={{ maxWidth: '820px', margin: '0 auto' }}>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '28px' }}>
          <button onClick={() => navigate('/tools')} style={{ background: 'transparent', border: '1px solid var(--border)', color: 'var(--text)', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>← Back</button>
          <span style={{ fontSize: '2rem' }}>❓</span>
          <h1 style={{ fontFamily: 'var(--font-heading)', fontWeight: 800, margin: 0 }}>DIP Knowledge Quiz</h1>
        </div>

        {/* INTRO */}
        {phase === 'intro' && (
          <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '40px', borderRadius: '24px', textAlign: 'center' }}>
            <div style={{ fontSize: '4rem', marginBottom: '24px' }}>🎯</div>
            <h2 style={{ fontFamily: 'var(--font-heading)', marginTop: 0, fontSize: '1.8rem' }}>Master the Fundamentals</h2>
            <p style={{ color: 'var(--text-dim)', maxWidth: '500px', margin: '0 auto 32px', lineHeight: 1.6 }}>Test your knowledge across all 5 modules. From bit-depth to wavelet transforms, see how much you've mastered.</p>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', maxWidth: '400px', margin: '0 auto 40px', textAlign: 'left' }}>
               <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '16px', border: '1px solid var(--border)' }}>
                 <div style={{ color: 'var(--blue)', fontWeight: 800, fontSize: '1.2rem' }}>{QUESTIONS.length}</div>
                 <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>QUESTIONS</div>
               </div>
               <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '16px', border: '1px solid var(--border)' }}>
                 <div style={{ color: 'var(--cyan)', fontWeight: 800, fontSize: '1.2rem' }}>10m</div>
                 <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>TIME LIMIT</div>
               </div>
            </div>

            <button onClick={() => setPhase('quiz')} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '16px 48px', borderRadius: '12px', fontWeight: 700, fontSize: '1.1rem', cursor: 'pointer', boxShadow: '0 10px 20px rgba(114, 9, 183, 0.3)' }}>
              🚀 Start Challenge
            </button>
          </div>
        )}

        {/* QUIZ */}
        {phase === 'quiz' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 700, letterSpacing: '0.1em' }}>PROGRESS</span>
                <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 800 }}>Question {current + 1} of {QUESTIONS.length}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 700, letterSpacing: '0.1em' }}>TIME LEFT</span>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.2rem', color: timeLeft < 60 ? 'var(--pink)' : 'var(--cyan)', fontWeight: 800 }}>{mm}:{ss}</div>
              </div>
            </div>
            
            <div style={{ background: 'rgba(255,255,255,0.05)', height: '8px', borderRadius: '4px', marginBottom: '32px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${((current) / QUESTIONS.length) * 100}%`, background: 'var(--blue)', borderRadius: '4px', transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)', boxShadow: '0 0 15px var(--blue)' }} />
            </div>

            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '32px', borderRadius: '24px' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', marginTop: 0, fontSize: '1.4rem', lineHeight: 1.4, marginBottom: '32px' }}>{QUESTIONS[current].q}</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
                {QUESTIONS[current].opts.map((opt, i) => (
                  <button key={i} onClick={() => selectOpt(i)} style={{
                    padding: '18px 24px', borderRadius: '16px', cursor: 'pointer', textAlign: 'left', fontFamily: 'var(--font-body)', fontSize: '1rem', fontWeight: 600, transition: 'all 0.2s',
                    background: selected === i ? 'var(--blue)' : 'rgba(255,255,255,0.02)',
                    border: '1px solid ' + (selected === i ? 'var(--blue)' : 'var(--border)'),
                    color: selected === i ? 'white' : 'var(--text)',
                    transform: selected === i ? 'translateX(8px)' : 'none'
                  }}>
                    <span style={{ marginRight: '16px', opacity: 0.5, fontSize: '0.8rem' }}>0{i+1}</span>{opt}
                  </button>
                ))}
              </div>
              <div style={{ marginTop: '40px', display: 'flex', justifyContent: 'flex-end' }}>
                <button onClick={next} disabled={selected === null} style={{ background: selected === null ? 'var(--border)' : 'var(--purple)', color: 'white', border: 'none', padding: '14px 40px', borderRadius: '12px', fontWeight: 700, cursor: selected === null ? 'not-allowed' : 'pointer', transition: 'all 0.3s' }}>
                  {current + 1 === QUESTIONS.length ? 'FINISH QUIZ' : 'NEXT QUESTION'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* REVIEW */}
        {phase === 'review' && (
          <div>
            <div style={{ background: 'var(--bg-glass)', border: '1px solid var(--border)', padding: '48px', borderRadius: '24px', textAlign: 'center', marginBottom: '32px', position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '4px', background: pct >= 70 ? 'var(--green)' : 'var(--pink)' }} />
              <div style={{ fontSize: '4rem', marginBottom: '16px' }}>{pct >= 90 ? '👑' : pct >= 70 ? '🌟' : pct >= 50 ? '📈' : '🛠️'}</div>
              <h2 style={{ fontFamily: 'var(--font-heading)', margin: '0 0 8px', fontSize: '2rem' }}>{pct}% Accuracy</h2>
              <p style={{ color: 'var(--text-dim)', marginBottom: '32px' }}>You answered {score} out of {QUESTIONS.length} correctly.</p>
              
              <button onClick={() => { setPhase('intro'); setCurrent(0); setAnswers(Array(QUESTIONS.length).fill(null)); setSelected(null); setTimeLeft(TOTAL_TIME) }} style={{ background: 'var(--purple)', color: 'white', border: 'none', padding: '12px 32px', borderRadius: '10px', fontWeight: 700, cursor: 'pointer' }}>
                🔄 Try Again
              </button>
            </div>

            <div style={{ display: 'grid', gap: '16px' }}>
              {QUESTIONS.map((q, i) => {
                const userAns = answers[i]
                const correct = userAns === q.ans
                return (
                  <div key={i} style={{ background: 'var(--bg-glass)', border: '1px solid ' + (correct ? 'rgba(6,214,160,0.2)' : 'rgba(255,51,102,0.2)'), padding: '24px', borderRadius: '16px', display: 'flex', gap: '20px' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: correct ? 'rgba(6,214,160,0.1)' : 'rgba(255,51,102,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      {correct ? '✅' : '❌'}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, marginBottom: '8px', fontSize: '1.05rem' }}>{q.q}</div>
                      {!correct && <div style={{ color: 'var(--pink)', fontSize: '0.85rem', marginBottom: '4px' }}>Your Answer: <span style={{ fontWeight: 600 }}>{userAns !== null ? q.opts[userAns] : 'None'}</span></div>}
                      <div style={{ color: 'var(--green)', fontSize: '0.85rem' }}>Correct Answer: <span style={{ fontWeight: 600 }}>{q.opts[q.ans]}</span></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
