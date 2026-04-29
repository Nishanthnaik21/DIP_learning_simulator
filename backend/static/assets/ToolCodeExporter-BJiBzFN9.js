import{a as F,r as s,g as A,j as e}from"./index-CnZ8LOBd.js";const x=(g,o)=>{const i=g||0;return o==="python"?{grayscale:`# Convert image to grayscale and adjust brightness
import cv2
import numpy as np

# Load image
img = cv2.imread('input.jpg')

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Adjust brightness by ${i}
result = np.clip(gray.astype(int) + ${i}, 0, 255).astype(np.uint8)

# Save result
cv2.imwrite('result.jpg', result)`,histogram_eq:`# Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
import cv2

# Load image in grayscale
img = cv2.imread('input.jpg', 0)

# Create CLAHE object with clip limit ${i}
clahe = cv2.createCLAHE(clipLimit=${i}.0, tileGridSize=(8,8))

# Apply CLAHE
result = clahe.apply(img)

# Save result
cv2.imwrite('result.jpg', result)`,gaussian_blur:`# Apply Gaussian Blur with variable kernel size
import cv2

# Load image
img = cv2.imread('input.jpg')

# Apply Gaussian blur with kernel size ${i}x${i}
result = cv2.GaussianBlur(img, (${i}, ${i}), 0)

# Save result
cv2.imwrite('result.jpg', result)`,canny_edge:`# Canny Edge Detection with variable threshold
import cv2

# Load image
img = cv2.imread('input.jpg', 0)

# Apply Canny detector with upper threshold ${i}
# Lower threshold is set to half of upper threshold
edges = cv2.Canny(img, ${i}/2, ${i})

# Save result
cv2.imwrite('result.jpg', edges)`,dft:`# Discrete Fourier Transform and spectrum visualization
import cv2
import numpy as np

# Load image in grayscale
img = cv2.imread('input.jpg', 0)

# Compute 2D DFT
f = np.fft.fft2(img)
fshift = np.fft.fftshift(f)

# Compute magnitude spectrum with log transform (gain ${i})
mag = ${i} * np.log(np.abs(fshift) + 1)

# Normalize to 0-255 range
result = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

# Save result
cv2.imwrite('result.jpg', result)`,morphology:`# Morphological Dilation
import cv2
import numpy as np

# Load image and threshold
img = cv2.imread('input.jpg', 0)
_, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

# Create 5x5 rectangular kernel
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

# Apply Dilation with ${i} iterations
result = cv2.dilate(binary, kernel, iterations=${i})

# Save result
cv2.imwrite('result.jpg', result)`,sobel:`# Sobel Edge Detection
import cv2
import numpy as np

# Load image in grayscale
img = cv2.imread('input.jpg', 0)

# Compute Sobel gradients in X and Y with kernel size ${i}
sx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=${i})
sy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=${i})

# Combine gradients to get magnitude
result = cv2.convertScaleAbs(np.sqrt(sx**2 + sy**2))

# Save result
cv2.imwrite('result.jpg', result)`,wavelet:`# Wavelet Image Compression
import cv2
import pywt
import numpy as np

# Load image as float
img = cv2.imread('input.jpg', 0).astype(float)

# Perform 2-level Haar Wavelet decomposition
coeffs = pywt.wavedec2(img, 'haar', level=2)

# Flatten and threshold coefficients (keep ${i}%)
all_coeffs = np.concatenate([c.flatten() for arr in coeffs[1:] for c in arr])
thresh = np.percentile(np.abs(all_coeffs), 100 - ${i})

# Reconstruct image from thresholded coefficients
rec = pywt.waverec2(coeffs, 'haar')
result = cv2.normalize(rec, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

# Save result
cv2.imwrite('result.jpg', result)`}:{grayscale:`% Grayscale and Brightness adjustment
img = imread('input.jpg');
gray = rgb2gray(img);

% Adjust brightness by ${i}
result = gray + ${i};
imwrite(result, 'result.jpg');`,histogram_eq:`% Histogram Equalization
img = imread('input.jpg');
gray = rgb2gray(img);

% Apply global equalization
result = histeq(gray);
imwrite(result, 'result.jpg');`,gaussian_blur:`% Gaussian Smoothing
img = imread('input.jpg');

% Create Gaussian filter of size ${i} with sigma 2.0
h = fspecial('gaussian', [${i} ${i}], 2.0);

% Apply filter
result = imfilter(img, h);
imwrite(result, 'result.jpg');`,canny_edge:`% Canny Edge Detection
img = imread('input.jpg');
gray = rgb2gray(img);

% Apply Canny with sensitivity threshold ${i/255}
result = edge(gray, 'Canny', ${i/255});
imwrite(result, 'result.jpg');`,dft:`% Frequency Domain DFT Spectrum
img = imread('input.jpg');
gray = double(rgb2gray(img));

% Compute centered FFT
F = fftshift(fft2(gray));

% Compute log-magnitude spectrum (gain ${i})
spec = ${i} * log(abs(F) + 1);

% Normalize and save
result = mat2gray(spec);
imwrite(result, 'result.jpg');`,sobel:`% Sobel Edge Detection
img = imread('input.jpg');
gray = rgb2gray(img);

% Compute Sobel edges
result = edge(gray, 'Sobel');
imwrite(result, 'result.jpg');`}},C={grayscale:{min:-100,max:100,step:1,default:0,label:"Brightness Offset"},histogram_eq:{min:1,max:10,step:1,default:2,label:"Contrast Limit"},gaussian_blur:{min:3,max:31,step:2,default:11,label:"Kernel Size (px)"},canny_edge:{min:10,max:250,step:5,default:150,label:"Upper Threshold"},dft:{min:1,max:50,step:1,default:20,label:"Spectrum Gain"},morphology:{min:1,max:10,step:1,default:1,label:"Dilation Iterations"},sobel:{min:1,max:7,step:2,default:3,label:"Sobel Kernel Size"},wavelet:{min:1,max:100,step:1,default:20,label:"Coeffs to Keep (%)"}};function O(){var w;const g=F(),[o,i]=s.useState("python"),[r,f]=s.useState("grayscale"),[n,y]=s.useState(0),[m,h]=s.useState(!1),[d,k]=s.useState(null),[c,R]=s.useState(null),[b,v]=s.useState(null),[z,j]=s.useState(!1),S=s.useRef(null),$=Object.keys(x(0,o)),u=((w=x(n,o))==null?void 0:w[r])||"# No snippet available",l=C[r]||{min:0,max:100,step:1,label:"Value"};s.useEffect(()=>{var t;y(((t=C[r])==null?void 0:t.default)||0)},[r]),s.useEffect(()=>{const t=setTimeout(()=>{d&&r&&L()},300);return()=>clearTimeout(t)},[d,r,n]);const I=t=>{var a;if((a=t.target.files)!=null&&a[0]){const p=t.target.files[0];k(p),R(URL.createObjectURL(p)),v(null)}},L=async()=>{if(!d)return;j(!0);const t=new FormData;t.append("file",d);let a="";r==="grayscale"||r==="negative"?(a="/api/module1/linear_operations",t.append("op","brightness"),t.append("value",n.toString())):r==="histogram_eq"?(a="/api/module2/histogram",t.append("method","clahe"),t.append("clip",n.toString())):r==="gaussian_blur"?(a="/api/module2/smoothing",t.append("ftype","gaussian"),t.append("ksize",n.toString()),t.append("sigma","2.0")):r==="canny_edge"?(a="/api/module5/edge_detection",t.append("detector","Canny"),t.append("t1",(n/2).toString()),t.append("t2",n.toString())):r==="dft"?(a="/api/module2/dft",t.append("view","magnitude")):r==="morphology"?(a="/api/module4/morphology",t.append("op","Dilation"),t.append("iters",n.toString())):r==="sobel"?(a="/api/module5/edge_detection",t.append("detector","Sobel (combined)"),t.append("ksize",n.toString())):r==="wavelet"&&(a="/api/module4/wavelets",t.append("wavelet","haar"),t.append("level","2"),t.append("keep_pct",n.toString()));try{const p=await A.post(a,t,{responseType:"blob"});v(URL.createObjectURL(p.data))}catch(p){console.error(p)}finally{j(!1)}},_=()=>{navigator.clipboard.writeText(u).then(()=>{h(!0),setTimeout(()=>h(!1),2e3)})},E=()=>{const t=new Blob([u],{type:"text/plain"}),a=document.createElement("a");a.href=URL.createObjectURL(t),a.download=`${r}.${o==="python"?"py":"m"}`,a.click()};return e.jsxs("div",{className:"with-navbar",style:{minHeight:"100vh",padding:"40px 32px 80px",background:"var(--bg)",color:"var(--text)"},children:[e.jsxs("div",{style:{maxWidth:"1150px",margin:"0 auto"},children:[e.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"12px",marginBottom:"28px"},children:[e.jsx("button",{onClick:()=>g("/tools"),style:{background:"transparent",border:"1px solid var(--border)",color:"var(--text)",padding:"6px 12px",borderRadius:"8px",cursor:"pointer"},children:"← Back"}),e.jsx("span",{style:{fontSize:"2rem"},children:"💻"}),e.jsx("h1",{style:{fontFamily:"var(--font-heading)",fontWeight:800,margin:0},children:"Code Exporter"})]}),e.jsxs("div",{style:{display:"grid",gridTemplateColumns:"380px 1fr",gap:"30px"},children:[e.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"20px"},children:[e.jsxs("div",{style:{background:"var(--bg-glass)",border:"1px solid var(--border)",padding:"24px",borderRadius:"24px"},children:[e.jsxs("h3",{style:{marginTop:0,marginBottom:"20px",fontFamily:"var(--font-heading)",fontSize:"1rem",display:"flex",alignItems:"center",gap:"8px"},children:[e.jsx("span",{style:{width:"24px",height:"24px",borderRadius:"50%",background:"var(--blue)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:"0.7rem",color:"white"},children:"1"}),"Input Image"]}),e.jsx("input",{type:"file",ref:S,onChange:I,accept:"image/*",style:{display:"none"}}),e.jsx("div",{onClick:()=>S.current.click(),style:{height:"160px",borderRadius:"16px",border:"2px dashed var(--border)",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",cursor:"pointer",overflow:"hidden",background:"rgba(255,255,255,0.02)",transition:"all 0.3s"},children:c?e.jsx("img",{src:c,style:{width:"100%",height:"100%",objectFit:"cover"}}):e.jsxs(e.Fragment,{children:[e.jsx("span",{style:{fontSize:"1.8rem",marginBottom:"8px"},children:"🖼️"}),e.jsx("span",{style:{fontSize:"0.75rem",color:"var(--text-dim)",fontWeight:600},children:"Click to upload image"})]})})]}),e.jsxs("div",{style:{background:"var(--bg-glass)",border:"1px solid var(--border)",padding:"24px",borderRadius:"24px"},children:[e.jsxs("h3",{style:{marginTop:0,marginBottom:"20px",fontFamily:"var(--font-heading)",fontSize:"1rem",display:"flex",alignItems:"center",gap:"8px"},children:[e.jsx("span",{style:{width:"24px",height:"24px",borderRadius:"50%",background:"var(--blue)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:"0.7rem",color:"white"},children:"2"}),"Operation"]}),e.jsx("div",{style:{display:"flex",gap:"8px",marginBottom:"20px",background:"rgba(0,0,0,0.2)",padding:"4px",borderRadius:"12px"},children:["python","matlab"].map(t=>e.jsx("button",{onClick:()=>{i(t),f(Object.keys(x(0,t))[0])},style:{flex:1,padding:"10px",border:"none",borderRadius:"10px",cursor:"pointer",fontWeight:800,fontSize:"0.7rem",transition:"all 0.3s",background:o===t?"var(--blue)":"transparent",color:o===t?"white":"var(--text-dim)",letterSpacing:"0.05em"},children:t.toUpperCase()},t))}),e.jsx("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"8px"},children:$.map(t=>e.jsx("button",{onClick:()=>f(t),style:{padding:"10px 8px",border:"none",borderRadius:"10px",cursor:"pointer",fontWeight:700,fontSize:"0.7rem",transition:"all 0.2s",background:r===t?"rgba(67,97,238,0.15)":"rgba(255,255,255,0.02)",color:r===t?"var(--blue)":"var(--text-dim)",border:"1px solid "+(r===t?"var(--blue)":"transparent"),textAlign:"center"},children:t.replace(/_/g," ").toUpperCase()},t))})]}),e.jsxs("div",{style:{background:"var(--bg-glass)",border:"1px solid var(--border)",padding:"24px",borderRadius:"24px"},children:[e.jsxs("h3",{style:{marginTop:0,marginBottom:"20px",fontFamily:"var(--font-heading)",fontSize:"1rem",display:"flex",alignItems:"center",gap:"8px"},children:[e.jsx("span",{style:{width:"24px",height:"24px",borderRadius:"50%",background:"var(--blue)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:"0.7rem",color:"white"},children:"3"}),"Parameters"]}),e.jsxs("div",{style:{marginBottom:"8px",display:"flex",justifyContent:"space-between"},children:[e.jsx("label",{style:{fontSize:"0.8rem",fontWeight:700,color:"var(--text-dim)"},children:l.label}),e.jsx("span",{style:{fontSize:"0.8rem",fontWeight:800,color:"var(--blue)"},children:n})]}),e.jsx("input",{type:"range",min:l.min,max:l.max,step:l.step,value:n,onChange:t=>y(Number(t.target.value)),style:{width:"100%",accentColor:"var(--blue)",cursor:"pointer"}}),e.jsxs("div",{style:{display:"flex",justifyContent:"space-between",marginTop:"6px",fontSize:"0.65rem",color:"var(--text-dim)",fontFamily:"var(--font-mono)"},children:[e.jsx("span",{children:l.min}),e.jsx("span",{children:l.max})]})]})]}),e.jsxs("div",{style:{display:"flex",flexDirection:"column",gap:"24px"},children:[e.jsxs("div",{style:{background:"var(--bg-glass)",border:"1px solid var(--border)",padding:"24px",borderRadius:"24px"},children:[e.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"16px"},children:[e.jsx("h3",{style:{margin:0,fontFamily:"var(--font-heading)",fontSize:"1.1rem",fontWeight:800},children:"Result Preview"}),z&&e.jsx("div",{style:{fontSize:"0.75rem",color:"var(--blue)",fontWeight:800,background:"rgba(67,97,238,0.1)",padding:"4px 12px",borderRadius:"20px",animation:"pulse 1.5s infinite"},children:"PROCESSING"})]}),e.jsxs("div",{style:{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"20px"},children:[e.jsxs("div",{children:[e.jsx("div",{style:{fontSize:"0.65rem",color:"var(--text-dim)",marginBottom:"8px",fontWeight:700,letterSpacing:"0.05em"},children:"ORIGINAL"}),e.jsx("div",{style:{background:"#000",borderRadius:"14px",overflow:"hidden",aspectRatio:"1/1",display:"flex",alignItems:"center",justifyContent:"center",border:"1px solid var(--border)"},children:c?e.jsx("img",{src:c,style:{maxWidth:"100%",maxHeight:"100%",objectFit:"contain"}}):e.jsx("span",{style:{color:"var(--text-dim)",fontSize:"0.8rem"},children:"No image uploaded"})})]}),e.jsxs("div",{children:[e.jsx("div",{style:{fontSize:"0.65rem",color:"var(--text-dim)",marginBottom:"8px",fontWeight:700,letterSpacing:"0.05em"},children:"PROCESSED"}),e.jsx("div",{style:{background:"#000",borderRadius:"14px",overflow:"hidden",aspectRatio:"1/1",display:"flex",alignItems:"center",justifyContent:"center",border:"1px solid var(--border)"},children:b?e.jsx("img",{src:b,style:{maxWidth:"100%",maxHeight:"100%",objectFit:"contain"}}):e.jsxs("div",{style:{textAlign:"center",padding:"20px"},children:[e.jsx("div",{style:{fontSize:"1.2rem",marginBottom:"8px"},children:"✨"}),e.jsx("div",{style:{fontSize:"0.7rem",color:"var(--text-dim)"},children:"Select operation to see result"})]})})]})]})]}),e.jsxs("div",{style:{background:"var(--bg-glass)",border:"1px solid var(--border)",borderRadius:"24px",overflow:"hidden",boxShadow:"0 20px 50px rgba(0,0,0,0.3)"},children:[e.jsxs("div",{style:{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"16px 24px",background:"rgba(0,0,0,0.4)",borderBottom:"1px solid var(--border)"},children:[e.jsxs("div",{style:{display:"flex",alignItems:"center",gap:"12px"},children:[e.jsx("div",{style:{display:"flex",gap:"5px"},children:[1,2,3].map(t=>e.jsx("div",{style:{width:"9px",height:"9px",borderRadius:"50%",background:t===1?"#ff5f56":t===2?"#ffbd2e":"#27c93f"}},t))}),e.jsxs("span",{style:{fontFamily:"var(--font-mono)",fontSize:"0.8rem",color:"var(--text-dim)",marginLeft:"10px",background:"rgba(255,255,255,0.05)",padding:"2px 10px",borderRadius:"4px"},children:[r,".",o==="python"?"py":"m"]})]}),e.jsxs("div",{style:{display:"flex",gap:"10px"},children:[e.jsx("button",{onClick:_,style:{background:m?"rgba(6,214,160,0.2)":"rgba(255,255,255,0.06)",color:m?"#06d6a0":"var(--text)",border:"none",padding:"8px 18px",borderRadius:"10px",cursor:"pointer",fontWeight:800,fontSize:"0.75rem",transition:"all 0.2s",display:"flex",alignItems:"center",gap:"6px"},children:m?"✅ COPIED":"📋 COPY CODE"}),e.jsx("button",{onClick:E,style:{background:"var(--blue)",color:"white",border:"none",padding:"8px 18px",borderRadius:"10px",cursor:"pointer",fontWeight:800,fontSize:"0.75rem",boxShadow:"0 4px 12px rgba(67, 97, 238, 0.3)"},children:"DOWNLOAD"})]})]}),e.jsxs("div",{style:{position:"relative"},children:[e.jsx("pre",{style:{margin:0,padding:"28px",fontFamily:"var(--font-mono)",fontSize:"0.88rem",lineHeight:1.8,color:"#a5d6ff",background:"#0d1117",overflowX:"auto",whiteSpace:"pre"},children:e.jsx("code",{children:u})}),e.jsx("div",{style:{position:"absolute",bottom:"15px",right:"20px",fontSize:"0.65rem",color:"rgba(255,255,255,0.15)",pointerEvents:"none"},children:"Dynamic Snippet Generator"})]})]})]})]})]}),e.jsx("style",{children:`
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
      `})]})}export{O as default};
