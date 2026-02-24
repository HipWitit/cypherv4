import streamlit as st
import re, os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & CSS ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

PEPPER = str(st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026")
U_MOD = 1114112
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

# CSS: proportional buttons using vh/em
st.markdown("""
    <style>
    .stApp { background-color: #DBDCFF !important; }
    div[data-testid="stWidgetLabel"], label { display: none !important; }

    /* Input Styling */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important;
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 1.2em !important;
        font-weight: 900 !important;
        border-radius: 15px !important;
        padding: 0.5em !important;
    }

    /* Buttons: proportional, flexible, same height */
    div.stButton > button {
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 15px !important;
        width: 90% !important;
        min-height: 8vh !important;       /* scales with viewport height */
        font-size: 1.6em !important;      /* scales with font */
        font-weight: 900 !important;
        text-transform: uppercase;
        margin: 1vh auto !important;      /* vertical spacing and center */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1) !important;
    }

    /* Result Box */
    .result-box {
        background-color: #FEE2E9; 
        color: #B4A7D6 !important;
        padding: 1em;
        border-radius: 12px;
        border: 3px solid #B4A7D6;
        word-wrap: break-word;
        font-weight: 900;
        font-family: "Courier New", monospace !important;
        font-size: 1.1em;
        margin-top: 1vh;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. ENGINE ---
def to_emoji(val): return "".join(EMOJI_MAP.get(d, d) for d in str(val))
def from_emoji(s): return int("".join(REV_MAP.get(c, c) for c in s))

def get_stable_params(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"uni_v5", iterations=100000, backend=default_backend())
    seed = int.from_bytes(hashlib.sha256(kdf.derive((kw + PEPPER).encode())).digest(), 'big')
    rng = random.Random(seed)
    a = rng.randint(3, 100000)
    while math.gcd(a, U_MOD) != 1: a += 1 
    return a, rng.randint(1000, 900000)

# --- 3. UI ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
if kw:
    st.progress(min(len(kw)/12, 1.0))

st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")
if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png")
user_input = st.text_area("Message", height=150, key="chem", placeholder="YOUR MESSAGE")

# --- 4. PROPORTIONAL BUTTONS ---
kiss_btn = st.button("KISS")
tell_btn = st.button("TELL")
destroy_btn = st.button("DESTROY CHEMISTRY")

if destroy_btn:
    st.session_state.lips = ""
    st.session_state.chem = ""
    st.session_state.hint = ""
    st.rerun()

# --- 5. PROCESSING ---
if kw and user_input:
    a, b = get_stable_params(kw)
    
    if kiss_btn:
        encoded = [to_emoji((a * ord(c) + b) % U_MOD) for c in user_input]
        st.markdown(f'<div class="result-box">{"  ".join(encoded)}</div>', unsafe_allow_html=True)
    
    if tell_btn:
        try:
            a_inv = pow(a, -1, U_MOD)
            parts = [p.strip() for p in user_input.split("  ") if p.strip()]
            decoded = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
            st.markdown(f'<div class="result-box">Whisper: {decoded}</div>', unsafe_allow_html=True)
        except:
            st.error("Chemistry Error! Check key or format.")

if os.path.exists("LPB.png"): st.image("LPB.png")
