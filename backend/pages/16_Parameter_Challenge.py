import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import numpy as np
import cv2
import random
from utils.theme import inject, page_header, theory_card, metric_row
from utils.helpers import upload_image, to_gray, normalize_display, psnr, comparison_slider

inject("Parameter Challenge", "🎯")


page_header("Parameter Challenge Mode",
            "MATCH THE TARGET IMAGE BY FINDING THE CORRECT PARAMETER VALUES", "🎯", "#4f8ef7")

# ── Theme injection ───────────────────────────────────────────────────────────
import sys as _sys2, os as _os2
_sys2.path.insert(0, _os2.path.join(_os2.path.dirname(__file__), ".."))
from utils.theme_manager import inject_theme as _inj, theme_toggle_button as _ttb
_inj()
del _sys2, _os2, _inj


theory_card(
    "Parameter Challenge tests your intuition about DIP operations. "
    "A target image is shown — it was produced by applying a specific operation with hidden parameters. "
    "Your goal is to adjust the sliders until your result matches the target. "
    "Score is based on PSNR similarity. Higher PSNR = closer match."
)

img_rgb = upload_image("challenge_up")
gray    = to_gray(img_rgb)

# ── Select challenge ───────────────────────────────────────────────────────────
st.markdown("### 🎯 Choose a Challenge")
challenge = st.selectbox("Challenge type", [
    "🔵 Gaussian Blur — find sigma",
    "🔴 Canny Edges — find thresholds",
    "🟢 Gamma Correction — find gamma",
    "🟡 CLAHE — find clip limit",
    "🟠 Threshold — find T value",
    "🔵 Laplacian sharpening — find weight",
    "🔴 DFT Low-pass — find cutoff D₀",
])

difficulty = st.radio("Difficulty", ["Easy (wide hint)", "Medium (narrow hint)", "Hard (no hint)"], horizontal=True)

# ── Session state for challenge ────────────────────────────────────────────────
ckey = f"challenge_{challenge}"
if ckey not in st.session_state or st.button("🔄 New Challenge"):
    rng = random.Random()
    if "Gaussian" in challenge:
        secret = round(rng.uniform(0.5, 15.0), 1)
    elif "Canny" in challenge:
        t1 = rng.randint(20, 150); secret = (t1, t1 * rng.randint(2, 4))
    elif "Gamma" in challenge:
        secret = round(rng.uniform(0.2, 3.5), 2)
    elif "CLAHE" in challenge:
        secret = round(rng.uniform(1.0, 8.0), 1)
    elif "Threshold" in challenge:
        secret = rng.randint(50, 220)
    elif "Laplacian" in challenge:
        secret = round(rng.uniform(0.3, 2.5), 2)
    else:  # DFT
        secret = rng.randint(10, 80)
    st.session_state[ckey] = secret
    st.session_state[f"{ckey}_attempts"] = 0
    st.session_state[f"{ckey}_best_psnr"] = 0.0

secret = st.session_state[ckey]
attempts = st.session_state.get(f"{ckey}_attempts", 0)
best_psnr = st.session_state.get(f"{ckey}_best_psnr", 0.0)

# ── Generate target image using secret ────────────────────────────────────────
def make_target(gray, challenge, secret):
    if "Gaussian" in challenge:
        return cv2.GaussianBlur(gray, (0,0), secret)
    elif "Canny" in challenge:
        t1, t2 = secret
        return cv2.Canny(gray, t1, t2)
    elif "Gamma" in challenge:
        lut = np.array([((i/255.0)**secret)*255 for i in range(256)], np.uint8)
        return cv2.LUT(gray, lut)
    elif "CLAHE" in challenge:
        clahe = cv2.createCLAHE(clipLimit=secret, tileGridSize=(8,8))
        return clahe.apply(gray)
    elif "Threshold" in challenge:
        _, out = cv2.threshold(gray, secret, 255, cv2.THRESH_BINARY)
        return out
    elif "Laplacian" in challenge:
        lap = cv2.Laplacian(gray.astype(np.float32), cv2.CV_32F)
        return np.clip(gray.astype(float) - secret * lap, 0, 255).astype(np.uint8)
    else:  # DFT
        rows,cols=gray.shape; crow,ccol=rows//2,cols//2
        Y,X=np.ogrid[:rows,:cols]; D=np.sqrt((Y-crow)**2+(X-ccol)**2)
        H=np.exp(-(D**2)/(2*secret**2))
        F=np.fft.fftshift(np.fft.fft2(gray.astype(float)))
        return normalize_display(np.abs(np.fft.ifft2(np.fft.ifftshift(F*H))))

target = make_target(gray, challenge, secret)

# ── Hint system ────────────────────────────────────────────────────────────────
def get_range(challenge, secret, difficulty):
    if "Gaussian" in challenge:
        full = (0.5, 15.0)
        if difficulty == "Easy (wide hint)":   r = (max(0.5, secret-4), min(15, secret+4))
        elif difficulty == "Medium (narrow hint)": r = (max(0.5, secret-2), min(15, secret+2))
        else: r = full
        return r, 0.1, "σ (sigma)"
    elif "Canny" in challenge:
        t1, t2 = secret
        return (max(10,t1-30), min(200,t1+30)), 1, "low threshold"
    elif "Gamma" in challenge:
        if difficulty=="Easy (wide hint)":   r=(max(0.1,secret-1.0),min(4.0,secret+1.0))
        elif difficulty=="Medium (narrow hint)": r=(max(0.1,secret-0.5),min(4.0,secret+0.5))
        else: r=(0.1,4.0)
        return r, 0.05, "γ (gamma)"
    elif "CLAHE" in challenge:
        if difficulty=="Easy (wide hint)":   r=(max(0.5,secret-2.0),min(10.0,secret+2.0))
        elif difficulty=="Medium (narrow hint)": r=(max(0.5,secret-1.0),min(10.0,secret+1.0))
        else: r=(0.5,10.0)
        return r, 0.1, "clip limit"
    elif "Threshold" in challenge:
        if difficulty=="Easy (wide hint)":   r=(max(0,secret-40),min(255,secret+40))
        elif difficulty=="Medium (narrow hint)": r=(max(0,secret-20),min(255,secret+20))
        else: r=(0,255)
        return r, 1, "T (threshold)"
    elif "Laplacian" in challenge:
        if difficulty=="Easy (wide hint)":   r=(max(0.0,secret-0.8),min(3.0,secret+0.8))
        elif difficulty=="Medium (narrow hint)": r=(max(0.0,secret-0.4),min(3.0,secret+0.4))
        else: r=(0.0,3.0)
        return r, 0.05, "weight w"
    else:  # DFT
        if difficulty=="Easy (wide hint)":   r=(max(5,secret-20),min(100,secret+20))
        elif difficulty=="Medium (narrow hint)": r=(max(5,secret-10),min(100,secret+10))
        else: r=(5,100)
        return r, 1, "D₀ cutoff"

param_range, step, param_label = get_range(challenge, secret, difficulty)

# ── Show layout ────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🎯 Target (match this)**")
    st.image(np.clip(target,0,255).astype(np.uint8), use_container_width=True, clamp=True)

with col3:
    st.markdown(f"**🏆 Best: {best_psnr:.1f} dB** | **Attempts: {attempts}**")
    # Score bar
    score_pct = min(100, best_psnr / 50 * 100)
    colour = "#22d3a5" if best_psnr > 35 else "#fbbf24" if best_psnr > 25 else "#f87171"
    st.markdown(f"""
    <div style="background:#1a2235;border-radius:6px;height:12px;margin:8px 0;overflow:hidden">
      <div style="width:{score_pct:.0f}%;height:100%;background:linear-gradient(90deg,{colour},{colour}88);
                  border-radius:6px;transition:width 0.5s"></div>
    </div>
    <div style="font-size:0.78rem;color:#64748b">
      {'🏆 Excellent match!' if best_psnr>40 else '✅ Good match!' if best_psnr>30 else '📈 Getting closer...' if best_psnr>20 else '💡 Keep adjusting...'}
    </div>""", unsafe_allow_html=True)
    if difficulty != "Hard (no hint)":
        st.markdown(f"""
        <div style="background:rgba(79,142,247,0.1);border:1px solid rgba(79,142,247,0.3);
                    border-radius:6px;padding:8px 12px;font-size:0.82rem;color:#93c5fd;margin-top:8px">
          💡 Hint: {param_label} is between <b>{param_range[0]}</b> and <b>{param_range[1]}</b>
        </div>""", unsafe_allow_html=True)

with col2:
    st.markdown("**⚙️ Your attempt**")
    # Main slider
    r_min, r_max = param_range
    if isinstance(secret, tuple):
        user_val = st.slider(f"Adjust {param_label}", int(r_min), int(r_max), int((r_min+r_max)/2), step=int(step))
        user_t2  = st.slider("high threshold", user_val*2, user_val*5, user_val*3)
        user_img = cv2.Canny(gray, user_val, user_t2)
    else:
        user_val = st.slider(f"Adjust {param_label}", float(r_min), float(r_max),
                             float((r_min+r_max)/2), step=float(step))
        user_img = make_target(gray, challenge, user_val)

    user_u8 = np.clip(user_img,0,255).astype(np.uint8)
    tgt_u8  = np.clip(target,0,255).astype(np.uint8)
    score   = psnr(tgt_u8, user_u8)
    st.image(user_u8, use_container_width=True, clamp=True)

    # Update best
    st.session_state[f"{ckey}_attempts"] = attempts + 1
    if score > best_psnr:
        st.session_state[f"{ckey}_best_psnr"] = score

    # Instant feedback colour
    fb_col = "#22d3a5" if score>35 else "#fbbf24" if score>25 else "#f87171"
    st.markdown(f"""
    <div style="background:{fb_col}18;border:1.5px solid {fb_col};border-radius:8px;
                padding:10px 16px;text-align:center;margin-top:8px">
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.3rem;color:{fb_col};font-weight:700">
        PSNR: {score:.1f} dB
      </div>
      <div style="font-size:0.78rem;color:#94a3b8;margin-top:2px">
        {'🏆 Perfect match!' if score>40 else '✅ Very close!' if score>35 else '📈 Almost there!' if score>25 else '💡 Keep adjusting'}
      </div>
    </div>""", unsafe_allow_html=True)

# ── Reveal answer ──────────────────────────────────────────────────────────────
st.markdown("---")
if st.checkbox("🔓 Reveal the secret parameter value"):
    reveal_val = f"({secret[0]}, {secret[1]})" if isinstance(secret,tuple) else str(secret)
    st.markdown(f"""
    <div style="background:rgba(168,85,247,0.12);border:2px solid #a855f7;border-radius:10px;
                padding:16px 20px;text-align:center">
      <div style="font-size:0.85rem;color:#c084fc;margin-bottom:6px">Secret {param_label}:</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:#a855f7;font-weight:700">
        {reveal_val}
      </div>
      <div style="font-size:0.78rem;color:#64748b;margin-top:6px">
        Your best attempt: {best_psnr:.1f} dB in {attempts} tries
      </div>
    </div>""", unsafe_allow_html=True)

# ── Comparison ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### ↔️ Your attempt vs Target")
comparison_slider(user_u8, tgt_u8, "Your attempt", "Target", key=f"chall_compare_{challenge[:8]}")
