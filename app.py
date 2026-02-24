import streamlit as st
import re, os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & REFINED CSS ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 

# Custom Emoji Map
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

st.markdown(f"""
    <style>
    /* Main App Background */
    .stApp {{ background-color: #DBDCFF !important; }}
    
    /* Ensure the container allows full width on mobile */
    .block-container {{
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    /* Hide Labels */
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}

    /* Input Boxes: Edge-to-Edge Bold Purple */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        -webkit-text-fill-color: #B4A7D6 !important;
        border-radius: 15px !important;
    }}

    /* THE STRETCH FIX: Force the button and its wrapper to 100% */
    div[data-testid="stButton"], 
    div[data-testid="stButton"] > button {{
        width: 100% !important;
        display: block !important;
    }}

    div[data-testid="stButton"] > button {{
        background-color: #B4A7D6 !important; 
        border-radius: 25px !important;
        height: 110px !important; 
        border: none !important;
        margin-top: 15px !important;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.2) !important;
    }}

    /* Giant Bold Pink Text targeting the internal paragraph */
    div[data-testid="stButton"] > button p {{
        color: #FFD4E5 !important;
        font-size: 55px !important; 
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", Gadget, sans-serif !important;
    }}

    /* Scale down the Destroy button text slightly so it doesn't wrap */
    div[data-testid="stButton"]:nth-of-type(3) > button p {{
        font-size: 30px !important;
    }}

    /* Result Box Style */
    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6 !important;
        padding: 25px;
        border-radius: 15px;
        border: 3px solid #B4A7D6;
        word-wrap: break-word;
        font-weight: 900;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 22px;
        margin-top: 25px;
        width: 100%;
    }}
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

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png", use_container_width=True)
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png", use_container_width=True)

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()

if kw:
    strength = min(len(kw) / 12.0, 1.0)
    st.progress(strength)

st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", use_container_width=True)
user_input = st.text_area("Message", height=150, key="chem", placeholder="YOUR MESSAGE")

# Button stacking
kiss_btn = st.button("KISS")
tell_btn = st.button("TELL")

if st.button("DESTROY CHEMISTRY"):
    for key in ["lips", "chem", "hint"]:
        if key in st.session_state: st.session_state[key] = ""
    st.rerun()

# --- 4. PROCESSING ---
if kw and user_input:
    a, b = get_stable_params(kw)
    
    if kiss_btn:
        encoded = [to_emoji((a * ord(c) + b) % U_MOD) for c in user_input]
        res = "  ".join(encoded) 
        st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

    if tell_btn:
        try:
            a_inv = pow(a, -1, U_MOD)
            parts = [p.strip() for p in user_input.split("  ") if p.strip()]
            decoded = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
            st.markdown(f'<div class="result-box">Whisper: {decoded}</div>', unsafe_allow_html=True)
        except:
            st.error("Chemistry Error! Check key or format.")

if os.path.exists("LPB.png"): st.image("LPB.png", use_container_width=True)
