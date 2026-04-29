import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import json
import io
import zipfile
from datetime import datetime
from PIL import Image
from utils.theme import inject, page_header, theory_card, metric_row
from utils.helpers import upload_image, to_gray, normalize_display, psnr, generate_pdf_report

inject("Session Recorder", "📊")


page_header("Session Recorder & Exporter",
            "TRACK ALL OPERATIONS, SAVE AS JSON/PDF/NOTEBOOK, RELOAD LATER", "📊", "#f87171")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "The Session Recorder tracks every DIP operation you add during a session. "
    "You can annotate each operation with notes, then export the complete session as: "
    "(1) JSON for reloading, (2) PDF lab report, (3) Jupyter notebook (.ipynb) with pre-filled code cells, "
    "(4) ZIP with all output images."
)

# ── Session state ──────────────────────────────────────────────────────────────
if "rec_ops" not in st.session_state:
    st.session_state["rec_ops"] = []
if "rec_student" not in st.session_state:
    st.session_state["rec_student"] = {"name":"","roll":"","module":""}

# ── Student info ───────────────────────────────────────────────────────────────
st.markdown("### 👤 Session Info")
c1, c2, c3 = st.columns(3)
st.session_state["rec_student"]["name"]   = c1.text_input("Name",   st.session_state["rec_student"]["name"])
st.session_state["rec_student"]["roll"]   = c2.text_input("Roll No",st.session_state["rec_student"]["roll"])
st.session_state["rec_student"]["module"] = c3.selectbox("Module", [
    "Module 1 — Fundamentals", "Module 2 — Spatial & Frequency",
    "Module 3 — Restoration",  "Module 4 — Color & Morphology",
    "Module 5 — Segmentation", "All Modules",
])

st.markdown("---")

# ── Add operation ──────────────────────────────────────────────────────────────
st.markdown("### ➕ Record a New Operation")
img_rgb = upload_image("rec_up")
gray    = to_gray(img_rgb)

with st.expander("Add operation to session", expanded=True):
    op_name = st.text_input("Operation name", placeholder="e.g. Gaussian Blur, Otsu Threshold...")
    theory  = st.text_area("Theory / Aim", placeholder="Explain what this operation does...", height=80)
    notes   = st.text_area("Observations", placeholder="What did you observe?", height=60)

    # Quick operation picker
    quick_op = st.selectbox("Quick apply (optional)", [
        "— choose —","Gaussian Blur","Median Filter","Canny Edges","CLAHE",
        "Otsu Threshold","Adaptive Threshold","Histogram EQ","Sobel","Laplacian",
        "Erosion","Dilation","Gamma Correction","Pseudo-colour","Harris Corners",
    ])

    params_q = {}
    before_q = gray.copy(); after_q = gray.copy()

    if quick_op == "Gaussian Blur":
        k=st.slider("k",3,31,9,2,key="rq1"); s=st.slider("σ",0.5,8.0,2.0,key="rq2")
        after_q=cv2.GaussianBlur(gray,(k,k),s); params_q={"ksize":k,"sigma":s}
    elif quick_op == "Median Filter":
        k=st.slider("k",3,21,5,2,key="rq3")
        after_q=cv2.medianBlur(gray,k); params_q={"ksize":k}
    elif quick_op == "Canny Edges":
        t1=st.slider("t1",10,200,50,key="rq4"); t2=st.slider("t2",50,400,150,key="rq5")
        after_q=cv2.Canny(gray,t1,t2); params_q={"t1":t1,"t2":t2}
    elif quick_op == "CLAHE":
        clip=st.slider("clip",1.0,8.0,2.5,key="rq6"); tile=st.slider("tile",4,16,8,key="rq7")
        clahe=cv2.createCLAHE(clipLimit=clip,tileGridSize=(tile,tile)); after_q=clahe.apply(gray); params_q={"clip":clip,"tile":tile}
    elif quick_op == "Otsu Threshold":
        T,after_q=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU); params_q={"auto_T":int(T)}
    elif quick_op == "Adaptive Threshold":
        block=st.slider("block",3,99,11,2,key="rq8"); C=st.slider("C",-30,30,2,key="rq9")
        after_q=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,block,C); params_q={"block":block,"C":C}
    elif quick_op == "Histogram EQ":
        after_q=cv2.equalizeHist(gray)
    elif quick_op == "Sobel":
        sx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3); sy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)
        after_q=cv2.convertScaleAbs(np.sqrt(sx**2+sy**2))
    elif quick_op == "Laplacian":
        after_q=cv2.convertScaleAbs(cv2.Laplacian(gray,cv2.CV_32F))
    elif quick_op in ("Erosion","Dilation"):
        k=st.slider("k",3,21,7,2,key="rq10")
        _,binary=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k))
        before_q=binary
        after_q=cv2.erode(binary,kernel) if quick_op=="Erosion" else cv2.dilate(binary,kernel); params_q={"ksize":k}
    elif quick_op == "Gamma Correction":
        g=st.slider("γ",0.1,4.0,1.5,key="rq11")
        lut=np.array([((i/255.0)**g)*255 for i in range(256)],np.uint8); after_q=cv2.LUT(gray,lut); params_q={"gamma":g}
    elif quick_op == "Pseudo-colour":
        pseudo=cv2.applyColorMap(gray,cv2.COLORMAP_JET); after_q=cv2.cvtColor(pseudo,cv2.COLOR_BGR2RGB)[:,:,0]
    elif quick_op == "Harris Corners":
        dst=cv2.cornerHarris(gray,2,3,0.04); overlay=cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
        overlay[cv2.dilate(dst,None)>0.01*dst.max()]=[255,50,50]; after_q=overlay[:,:,0]

    if quick_op != "— choose —":
        before_u8 = np.clip(before_q,0,255).astype(np.uint8)
        after_u8  = np.clip(after_q,0,255).astype(np.uint8)
        c1p,c2p=st.columns(2)
        with c1p: st.markdown("**Before**"); st.image(before_u8,use_container_width=True,clamp=True)
        with c2p: st.markdown("**After**");  st.image(after_u8,use_container_width=True,clamp=True)

        bg=before_u8 if len(before_u8.shape)==2 else cv2.cvtColor(before_u8,cv2.COLOR_RGB2GRAY)
        ag=after_u8  if len(after_u8.shape)==2  else cv2.cvtColor(after_u8,cv2.COLOR_RGB2GRAY)
        p=psnr(bg,ag)
        st.metric("PSNR",f"{p:.1f} dB")

        if not op_name: op_name = quick_op
        if not theory:  theory  = f"Applied {quick_op} to the input image."

    if st.button("📥 Add to Session"):
        if op_name:
            b_img = np.clip(before_q,0,255).astype(np.uint8)
            a_img = np.clip(after_q,0,255).astype(np.uint8)
            bg2   = b_img if len(b_img.shape)==2 else cv2.cvtColor(b_img,cv2.COLOR_RGB2GRAY)
            ag2   = a_img if len(a_img.shape)==2 else cv2.cvtColor(a_img,cv2.COLOR_RGB2GRAY)
            st.session_state["rec_ops"].append({
                "title":     op_name,
                "theory":    theory,
                "notes":     notes,
                "params":    params_q if params_q else {},
                "psnr":      round(psnr(bg2,ag2),2),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "before_img": b_img.tolist(),
                "after_img":  a_img.tolist(),
            })
            st.success(f"✅ '{op_name}' added! Session has {len(st.session_state['rec_ops'])} operations.")
            st.rerun()
        else:
            st.warning("Please enter an operation name.")

# ── Session log ────────────────────────────────────────────────────────────────
st.markdown("---")
ops = st.session_state["rec_ops"]
st.markdown(f"### 📋 Session Log — {len(ops)} operation(s)")

if ops:
    for i, op in enumerate(ops):
        with st.expander(f"#{i+1} {op['title']} @ {op['timestamp']} · PSNR: {op['psnr']} dB"):
            c1,c2,c3 = st.columns([2,2,3])
            with c1:
                b_arr = np.array(op["before_img"],dtype=np.uint8)
                st.image(b_arr, caption="Before", use_container_width=True, clamp=True)
            with c2:
                a_arr = np.array(op["after_img"],dtype=np.uint8)
                st.image(a_arr, caption="After", use_container_width=True, clamp=True)
            with c3:
                st.markdown(f"**Theory:** {op['theory']}")
                if op["notes"]: st.markdown(f"**Observations:** {op['notes']}")
                if op["params"]: st.json(op["params"])

            if st.button(f"🗑️ Remove", key=f"del_rec_{i}"):
                st.session_state["rec_ops"].pop(i); st.rerun()

    if st.button("🗑️ Clear entire session"):
        st.session_state["rec_ops"] = []; st.rerun()

    # ── Export options ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📤 Export Session")
    export_type = st.radio("Export format", ["JSON", "PDF Lab Report", "Jupyter Notebook", "ZIP (all images)"], horizontal=True)

    student = st.session_state["rec_student"]

    if export_type == "JSON":
        # Strip image arrays for JSON (too large)
        ops_json = [{k:v for k,v in op.items() if k not in ("before_img","after_img")} for op in ops]
        data = {"student":student,"timestamp":datetime.now().isoformat(),"operations":ops_json}
        json_str = json.dumps(data, indent=2)
        st.download_button("⬇ Download JSON", json_str,
                           f"session_{student['roll'] or 'student'}.json","application/json")

    elif export_type == "PDF Lab Report":
        pdf_ops = [{
            "title":      op["title"],
            "theory":     op["theory"] + (" Observations: "+op["notes"] if op["notes"] else ""),
            "parameters": op["params"],
            "before_img": np.array(op["before_img"],dtype=np.uint8),
            "after_img":  np.array(op["after_img"],dtype=np.uint8),
            "metrics":    {"PSNR": f"{op['psnr']} dB", "Timestamp": op["timestamp"]},
        } for op in ops]
        if st.button("🖨️ Generate PDF"):
            pdf = generate_pdf_report(pdf_ops, student["name"], student["roll"], student["module"])
            if pdf:
                st.download_button("⬇ Download PDF", pdf,
                                   f"lab_{student['roll'] or 'student'}.pdf","application/pdf")

    elif export_type == "Jupyter Notebook":
        cells = [
            {"cell_type":"markdown","metadata":{},"source":[f"# DIP Lab Session\n**Student:** {student['name']} | **Roll:** {student['roll']} | **Module:** {student['module']}"]},
            {"cell_type":"code","metadata":{},"source":["import cv2\nimport numpy as np\nimport matplotlib.pyplot as plt\n\nimg = cv2.imread('your_image.jpg', cv2.IMREAD_GRAYSCALE)\n"],"outputs":[],"execution_count":None},
        ]
        for i, op in enumerate(ops):
            cells.append({"cell_type":"markdown","metadata":{},"source":[f"## Experiment {i+1}: {op['title']}\n{op['theory']}"]})
            code_lines = [f"# {op['title']}"]
            for k,v in op["params"].items():
                code_lines.append(f"{k} = {v!r}")
            code_lines += ["# Add your processing code here", "result = img.copy()  # replace with actual operation", "plt.imshow(result, cmap='gray'); plt.title(f'{op['title']}'); plt.show()"]
            cells.append({"cell_type":"code","metadata":{},"source":["\n".join(code_lines)],"outputs":[],"execution_count":None})
        nb = {"nbformat":4,"nbformat_minor":5,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"}},"cells":cells}
        nb_str = json.dumps(nb, indent=2)
        st.download_button("⬇ Download .ipynb", nb_str,
                           f"dip_session_{student['roll'] or 'student'}.ipynb","application/json")

    else:  # ZIP
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf,"w",zipfile.ZIP_DEFLATED) as zf:
            for i, op in enumerate(ops):
                for prefix, key in [("before","before_img"),("after","after_img")]:
                    arr = np.array(op[key],dtype=np.uint8)
                    pil = Image.fromarray(arr)
                    buf = io.BytesIO(); pil.save(buf,"PNG"); buf.seek(0)
                    safe = op["title"].replace(" ","_").replace("/","_")[:20]
                    zf.writestr(f"{i+1:02d}_{safe}_{prefix}.png", buf.read())
            ops_txt = "\n".join([f"#{i+1} {op['title']} | PSNR:{op['psnr']} | {op['timestamp']}" for i,op in enumerate(ops)])
            zf.writestr("session_log.txt", ops_txt)
        zip_buf.seek(0)
        st.download_button("⬇ Download ZIP", zip_buf,
                           f"session_images_{student['roll'] or 'student'}.zip","application/zip")
else:
    st.info("No operations recorded yet. Add operations using the panel above.")
