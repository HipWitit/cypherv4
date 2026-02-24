import streamlit as st
import re, os, random, hashlib, base64, math
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & AGGRESSIVE STYLING ---
st.set_page_config(page_title="Cyfer Pro: Unicode Global", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 

# Mapping
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}

    /* Fix Text Colors - Forcing Purple on Pink */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}

    /* FORCE HORIZONTAL BUTTONS */
    [data-testid="column"] {{
        width: 48% !important;
        flex: 1 1 48% !important;
        min-width: 48% !important;
    }}
    
    div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }}

    .stButton > button {{
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 20px !important;
        min-height: 60px !important; 
        border: none !important;
        text-transform: uppercase;
        font-size: 22px !important; 
        font-weight: 800 !important;
    }}

    /* Result Box Purple Text */
    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6 !important;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #B4A7D6;
        word-wrap: break-word;
        font-weight: bold;
        font-family: "Courier New", Courier, monospace !important;
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

# --- 3. UI ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")

# Key & Progress
kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
if kw:
    strength = min(len(kw) / 12.0, 1.0)
    st.progress(strength)

st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# The Side-by-Side Grid
col1, col2 = st.columns(2)
kiss_btn = col1.button("KISS")
tell_btn = col2.button("TELL")

# Fixed Destroy Button
if st.button("DESTROY CHEMISTRY", use_container_width=True):
    st.session_state.lips = ""
    st.session_state.chem = ""
    st.session_state.hint = ""
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
            st.error("Chemistry Error! Try again.")
