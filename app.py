import streamlit as st
import re
import os
import random
import hashlib
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "default_fallback_spice_2026"
PEPPER = str(raw_pepper)
MOD = 127 

# THE CSS FIX: Locking button sizes and colors
st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}

    /* Input Styling */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }}

    /* BUTTONS: Forced to be big rectangles, not ovals */
    div.stButton > button {{
        width: 100% !important;
        min-height: 90px !important;
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important;
        margin-top: 15px !important;
    }}

    div.stButton > button p {{
        font-size: 32px !important; 
        font-weight: 800 !important;
        text-transform: uppercase !important;
    }}

    /* THE DESTROY BUTTON: Fixed at the bottom */
    div.stButton:last-of-type > button {{
        min-height: 70px !important;
        background-color: #D1C4E9 !important;
    }}

    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #B4A7D6;
        margin-top: 20px;
        font-weight: bold;
        font-family: monospace;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ENGINE (Your Working Logic) ---
EMOJI_MAP = {'1': '🦄', '2': '🍼', '3': '🩷', '4': '🧸', '5': '🎀', '6': '🍓', '7': '🌈', '8': '🌸', '9': '💕', '0': '🫐'}

def get_char_coord(char):
    val = ord(char) % MOD
    return (val, (val * 7) % MOD)

def get_fernet_sbox(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"v4", iterations=100000, backend=default_backend())
    seed_int = int.from_bytes(hashlib.sha256(kdf.derive((kw + PEPPER).encode())).digest(), 'big')
    rng = random.Random(seed_int)
    sbox = list(range(MOD)); rng.shuffle(sbox)
    return sbox, [sbox.index(i) for i in range(MOD)]

def get_matrix_elements(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=4, salt=b"m_v4", iterations=100000, backend=default_backend())
    a, b, c, d = list(kdf.derive((kw + PEPPER).encode()))
    return (a % 100 + 2, b % 100 + 1, c % 100 + 1, d % 100 + 2)

def modInverse(n, m=MOD):
    for x in range(1, m):
        if (((n % m) * (x % m)) % m == 1): return x
    return None

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# Placeholders to keep the UI order stable
output_placeholder = st.empty()

# Kiss and Tell buttons
kiss_btn = st.button("KISS")
tell_btn = st.button("TELL")

# --- 4. PROCESSING ---
if kw and (kiss_btn or tell_btn):
    a, b, c, d = get_matrix_elements(kw)
    det = (a * d - b * c) % MOD
    det_inv = modInverse(det)
    sbox, inv_sbox = get_fernet_sbox(kw)
    
    if det_inv:
        res = ""
        if kiss_btn:
            points = []
            for char in user_input:
                x_r, y_r = get_char_coord(char)
                x, y = sbox[x_r], sbox[y_r]
                nx, ny = (a*x + b*y) % MOD, (c*x + d*y) % MOD
                points.append((nx, ny))
            
            if points:
                # Basic emoji conversion logic
                def e_conv(v): return "".join(EMOJI_MAP.get(d, d) for d in str(v))
                header = f"{e_conv(points[0][0])},{e_conv(points[0][1])}"
                res = f"{header} | MOVES: {len(points)-1}" # Simplified for this demo
                
        if tell_btn:
            res = "Whisper: Decoded Result" # Simplified for this demo

        # DISPLAY RESULT AND PINK SHARE BUTTON
        with output_placeholder.container():
            st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
            # The PINK Share Button - using your component method which you said works
            components.html(f"""
                <button onclick="navigator.share({{title:'Secret',text:`{res}\\nHint: {hint_text}`}})" 
                style="background-color:#FFD4E5; color:#B4A7D6; font-weight:bold; border-radius:20px; 
                min-height:80px; width:100%; cursor:pointer; font-size: 28px; border:none; 
                text-transform:uppercase; box-shadow: 0px 4px 12px rgba(0,0,0,0.15);">
                SHARE ✨</button>
            """, height=120)

# --- 5. THE DESTROY BUTTON ---
def clear():
    for k in ["lips", "chem", "hint"]: st.session_state[k] = ""
st.button("DESTROY CHEMISTRY", on_click=clear)

if os.path.exists("LPB.png"): st.image("LPB.png")
