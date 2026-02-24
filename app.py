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

st.markdown(f"""
    <style>
    /* Background and global styles */
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}

    /* TEXT BOX & INPUT - DARK PURPLE TEXT */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #7E60BF !important; /* Darker purple for readability */
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }}
    
    /* Input placeholder styling */
    input::placeholder, textarea::placeholder {{
        color: #B4A7D6 !important;
        opacity: 0.8;
    }}

    /* ACTION BUTTONS (KISS, TELL) - RECTANGLE FIX */
    div.stButton > button {{
        width: 100% !important;
        min-height: 90px !important; /* Forces rectangle height */
        min-width: 250px !important; /* Forces rectangle width */
        background-color: #7E60BF !important; /* Deeper Purple */
        color: #FFE1EB !important; /* Bright Pink Text */
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0px 5px 0px #5E448F !important; /* 3D effect shadow */
        margin-top: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div.stButton > button p {{
        font-size: 32px !important; 
        font-weight: 800 !important;
        letter-spacing: 2px;
        margin: 0 !important;
    }}

    /* DESTROY BUTTON - DIFFERENT STYLE */
    div.stButton:last-of-type > button {{
        min-height: 60px !important;
        background-color: #B4A7D6 !important;
        box-shadow: 0px 4px 0px #8E7DB3 !important;
        margin-top: 30px !important;
    }}
    
    div.stButton:last-of-type > button p {{
        font-size: 20px !important;
    }}

    /* RESULT BOX */
    .result-box {{
        background-color: #FEE2E9; 
        color: #7E60BF;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #7E60BF;
        margin-top: 20px;
        font-weight: bold;
        font-family: monospace;
        text-align: center;
        word-break: break-all;
        font-size: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE ---
EMOJI_MAP = {'1': '🦄', '2': '🍼', '3': '🩷', '4': '🧸', '5': '🎀', '6': '🍓', '7': '🌈', '8': '🌸', '9': '💕', '0': '🫐'}

def get_char_coord(char):
    val = ord(char) % MOD
    return (val, (val * 7) % MOD)

def get_fernet_sbox(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"stable_v4", iterations=100000, backend=default_backend())
    derived = kdf.derive((kw + PEPPER).encode())
    seed = int.from_bytes(hashlib.sha256(derived).digest(), 'big')
    rng = random.Random(seed)
    sbox = list(range(MOD))
    rng.shuffle(sbox)
    return sbox, [sbox.index(i) for i in range(MOD)]

def get_matrix_elements(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=4, salt=b"matrix_v4", iterations=100000, backend=default_backend())
    a, b, c, d = list(kdf.derive((kw + PEPPER).encode()))
    return (a % 100 + 2, b % 100 + 1, c % 100 + 1, d % 100 + 2)

def modInverse(n, m=MOD):
    for x in range(1, m):
        if (((n % m) * (x % m)) % m == 1): return x
    return None

def apply_sweet_parity(val_str):
    def replacer(match):
        digit = match.group(2)
        return ('🍭' if int(digit) % 2 == 0 else '🍬') + digit
    return re.sub(r'(-)(\d)', replacer, val_str)

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()

# Chemistry Level Bar
if kw:
    strength = min((len(kw) / 12.0) + (0.1 if any(c.isdigit() for c in kw) else 0), 1.0)
    st.write(f"🧪 **CHEMISTRY LEVEL:** {int(strength*100)}%")
    st.progress(strength)
else:
    st.write("🧪 **CHEMISTRY LEVEL:** 0%")
    st.progress(0.0)

hint_text = st
