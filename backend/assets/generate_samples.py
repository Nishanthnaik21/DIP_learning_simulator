"""
Generate classic DIP test images programmatically (no downloads needed).
Run once: python3 assets/generate_samples.py
"""
import cv2
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), "samples")
os.makedirs(OUT, exist_ok=True)

def save(name, img):
    cv2.imwrite(os.path.join(OUT, name), img)
    print(f"  saved: {name}")

# ── 1. Cameraman (synthetic) ──────────────────────────────────────────────────
def cameraman():
    img = np.ones((256,256), np.uint8)*190
    # Sky gradient
    for i in range(100): img[i,:] = int(220 - i*0.5)
    # Ground
    img[180:,:] = 80
    img[160:180,:] = 120
    # Tripod
    cv2.line(img,(128,200),(110,245),(40,2)); cv2.line(img,(128,200),(128,245),(40,2)); cv2.line(img,(128,200),(146,245),(40,2))
    # Body
    cv2.rectangle(img,(108,155),(148,205),(50,-1))
    # Head
    cv2.circle(img,(128,145),18,(60,-1))
    # Camera
    cv2.rectangle(img,(118,148),(138,158),(30,-1))
    cv2.circle(img,(128,153),4,(200,-1))
    # Legs
    cv2.line(img,(118,205),(112,245),(40,2)); cv2.line(img,(138,205),(144,245),(40,2))
    save("cameraman.png", img)

# ── 2. Lena (colorful synthetic) ─────────────────────────────────────────────
def lena_synthetic():
    img = np.zeros((256,256,3),np.uint8)
    # Background
    img[:,:] = [200,180,160]
    # Hat
    cv2.ellipse(img,(128,60),(80,30),0,0,360,(180,100,80),-1)
    cv2.rectangle(img,(60,45),(196,75),(160,80,60),-1)
    # Feather
    for i in range(20): cv2.line(img,(150+i,45),(170+i,20),(220,200,180),1)
    # Face
    cv2.ellipse(img,(128,130),(55,65),0,0,360,(220,190,160),-1)
    # Eyes
    cv2.ellipse(img,(108,115),(10,7),0,0,360,(80,60,40),-1)
    cv2.ellipse(img,(148,115),(10,7),0,0,360,(80,60,40),-1)
    cv2.circle(img,(108,115),4,(40,30,20),-1); cv2.circle(img,(148,115),4,(40,30,20),-1)
    cv2.circle(img,(110,113),2,(255,255,255),-1); cv2.circle(img,(150,113),2,(255,255,255),-1)
    # Nose
    cv2.ellipse(img,(128,135),(8,5),0,0,360,(200,165,140),-1)
    # Lips
    cv2.ellipse(img,(128,155),(18,8),0,0,360,(180,100,100),-1)
    cv2.ellipse(img,(128,152),(18,5),0,180,360,(220,170,160),-1)
    # Shoulder
    cv2.ellipse(img,(128,230),(90,50),0,0,180,(160,120,100),-1)
    # Hair
    cv2.ellipse(img,(128,100),(60,50),0,180,360,(80,50,30),-1)
    save("lena.png", img)

# ── 3. Coins (for morphology) ─────────────────────────────────────────────────
def coins():
    img = np.ones((256,256),np.uint8)*50
    positions = [(60,60,35),(150,70,28),(70,160,32),(170,155,40),(115,115,22),(220,200,25),(35,210,20)]
    for (cx,cy,r) in positions:
        cv2.circle(img,(cx,cy),r,200,-1)
        cv2.circle(img,(cx,cy),r-4,180,-1)
        cv2.circle(img,(cx,cy),r-8,200,-1)
        cv2.circle(img,(cx,cy),r,100,2)
    img = cv2.GaussianBlur(img,(3,3),0.5)
    save("coins.png", img)

# ── 4. Circuit board (for edge detection) ─────────────────────────────────────
def circuit():
    img = np.zeros((256,256),np.uint8)+30
    # Traces
    for y in range(20,256,25):
        cv2.line(img,(0,y),(256,y),90,2)
    for x in range(20,256,25):
        cv2.line(img,(x,0),(x,256),90,2)
    # Components
    for (x,y) in [(50,50),(120,80),(200,50),(60,150),(180,160),(130,200)]:
        cv2.rectangle(img,(x-15,y-10),(x+15,y+10),180,-1)
        cv2.rectangle(img,(x-15,y-10),(x+15,y+10),220,1)
    # Vias
    for (x,y) in [(80,120),(160,100),(100,200),(220,180)]:
        cv2.circle(img,(x,y),6,200,-1); cv2.circle(img,(x,y),3,50,-1)
    img = cv2.GaussianBlur(img,(3,3),0.5)
    save("circuit.png", img)

# ── 5. Baboon (colorful, for color processing) ───────────────────────────────
def baboon():
    img = np.zeros((256,256,3),np.uint8)
    # Brown face base
    img[:,:] = [100,80,60]
    # Fur texture
    rng = np.random.RandomState(42)
    noise = rng.randint(-20,20,(256,256,3))
    img = np.clip(img.astype(int)+noise,0,255).astype(np.uint8)
    # Blue cheeks
    cv2.ellipse(img,(80,140),(35,25),0,0,360,(180,80,20),-1)
    cv2.ellipse(img,(176,140),(35,25),0,0,360,(180,80,20),-1)
    # Red nose
    cv2.ellipse(img,(128,155),(30,20),0,0,360,(30,30,200),-1)
    # Eyes
    cv2.circle(img,(95,110),15,(40,30,20),-1); cv2.circle(img,(161,110),15,(40,30,20),-1)
    cv2.circle(img,(95,110),8,(20,15,10),-1); cv2.circle(img,(161,110),8,(20,15,10),-1)
    cv2.circle(img,(97,108),3,(255,255,255),-1); cv2.circle(img,(163,108),3,(255,255,255),-1)
    # Fur around face
    for i in range(60):
        angle = rng.uniform(0,2*np.pi); r = rng.randint(100,130)
        x,y = int(128+r*np.cos(angle)), int(128+r*np.sin(angle))
        clr = (int(rng.uniform(60,120)),int(rng.uniform(50,100)),int(rng.uniform(20,60)))
        cv2.circle(img,(x,y),rng.randint(3,8),clr,-1)
    save("baboon.png", img)

# ── 6. Checkerboard (for sampling demo) ──────────────────────────────────────
def checkerboard():
    img = np.zeros((256,256),np.uint8)
    for i in range(8):
        for j in range(8):
            if (i+j)%2==0:
                img[i*32:(i+1)*32, j*32:(j+1)*32] = 255
    save("checkerboard.png", img)

# ── 7. Gradient ramp (for quantization demo) ─────────────────────────────────
def gradient_ramp():
    img = np.zeros((256,256),np.uint8)
    for i in range(256): img[:,i] = i
    save("gradient_ramp.png", img)

# ── 8. Text document (for thresholding demo) ─────────────────────────────────
def text_doc():
    img = np.ones((256,256),np.uint8)*240
    # Simulate uneven illumination
    for i in range(256):
        for j in range(256):
            img[i,j] = max(0,min(255, img[i,j] - int(40*(i/256)**2) - int(30*(j/256)**2)))
    texts = ["Digital Image","Processing","Module 22AIM61","OpenCV + NumPy","Streamlit App"]
    for idx,t in enumerate(texts):
        cv2.putText(img, t, (15, 35+idx*42), cv2.FONT_HERSHEY_SIMPLEX, 0.55, 30, 1, cv2.LINE_AA)
    save("text_doc.png", img)

# ── 9. X-ray style (for restoration demo) ────────────────────────────────────
def xray_style():
    img = np.zeros((256,256),np.uint8)+40
    # Rib cage simulation
    for i,y in enumerate(range(60,200,18)):
        pts = np.array([[60,y],[80,y-5],[128,y-8],[176,y-5],[196,y]], np.int32)
        cv2.polylines(img,[pts],False,min(255,160-i*5),3)
        pts2 = pts.copy(); pts2[:,1] += 10
        cv2.polylines(img,[pts2],False,min(255,150-i*5),2)
    # Spine
    for y in range(50,210,12):
        cv2.rectangle(img,(116,y),(140,y+9),180,-1)
        cv2.rectangle(img,(116,y),(140,y+9),200,1)
    # Lung fields
    cv2.ellipse(img,(90,130),(40,60),0,0,360,80,-1)
    cv2.ellipse(img,(166,130),(40,60),0,0,360,80,-1)
    img = cv2.GaussianBlur(img,(5,5),1)
    noise = np.random.randint(0,15,img.shape,np.uint8)
    img = cv2.add(img,noise)
    save("xray.png", img)

# ── 10. Aerial/satellite style ────────────────────────────────────────────────
def satellite():
    rng = np.random.RandomState(7)
    img = np.zeros((256,256,3),np.uint8)
    img[:,:] = [60,100,40]   # green base
    # Roads
    cv2.line(img,(0,128),(256,128),(80,80,80),8)
    cv2.line(img,(128,0),(128,256),(80,80,80),8)
    # Buildings
    for _ in range(20):
        x,y = rng.randint(10,230), rng.randint(10,230)
        w,h = rng.randint(10,30), rng.randint(10,30)
        shade = rng.randint(100,180)
        img[y:y+h,x:x+w] = [shade,shade-10,shade-20]
    # Water body
    cv2.ellipse(img,(50,200),(40,30),0,0,360,(120,100,40),-1)
    # Trees (random dark green dots)
    for _ in range(60):
        x,y = rng.randint(0,256), rng.randint(0,256)
        cv2.circle(img,(x,y),rng.randint(2,6),(30,70+rng.randint(0,40),20),-1)
    save("satellite.png", img)

print("Generating sample images...")
cameraman(); lena_synthetic(); coins(); circuit(); baboon()
checkerboard(); gradient_ramp(); text_doc(); xray_style(); satellite()
print("All 10 samples generated in assets/samples/")
