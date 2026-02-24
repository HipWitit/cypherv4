import streamlit as st
import os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & STABLE CSS ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 

EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

# Memorize the result so it doesn't vanish
if "out" not in st.session_state:
    st.session_state.out = ""

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    
    /* Input Boxes */
    .stTextInput input, .stTextArea textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 20px !important; font-weight: 900 !important;
        border-radius: 15px !important;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}

    /* THE BUTTON FIX: No flex, no columns, just blocks */
    div.stButton > button, div.stDownloadButton > button {{
        width: 100% !important;
        height: 80px !important;
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important;
        margin-bottom: 10px !important;
    }}

    div.stButton > button p, div.stDownloadButton > button p {{
        font-size: 30px !important; 
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", sans-serif !important;
    }}

    /* Result Box */
    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6 !important;
        padding: 20px;
        border-radius: 20px;
        border: 4px solid #B4A7D6;
        word-wrap: break-word;
        font-family: "Courier New", monospace !important;
        font-size: 22px;
        margin-bottom: 15px;
        text-align: center;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE ---
def to_emoji(val): return "".join(EMOJI_MAP.get(d, d) for d in str(val))
def from_emoji(s):
    res = "".join(REV_MAP[char] for char in s if char in REV_MAP)
    return int(res) if res else 0

def get_params(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"uni_v5", iterations=100000, backend=default_backend())
    seed = int.from_bytes(hashlib.sha256(kdf.derive((kw + PEPPER).encode())).digest(), 'big')
    rng = random.Random(seed)
    a = rng.randint(3, 100000)
    while math.gcd(a, U_MOD) != 1: a += 1 
    return a, rng.randint(1000, 900000)

# --- 3. UI ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png", width=600)
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png", width=600)

kw = st.text_input("K", type="password", key="lips", placeholder="SECRET KEY")
st.text_input("H", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", width=600)
user_input = st.text_area("M", height=120, key="chem", placeholder="YOUR MESSAGE")

# Logic
if kw and user_input:
    a, b = get_params(kw)
    if st.button("KISS"):
        encoded = [to_emoji((a * ord(c) + b) % U_MOD) for c in user_input]
        st.session_state.out = "  ".join(encoded)
    
    if st.button("TELL"):
        try:
            a_inv = pow(a, -1, U_MOD)
            parts = [p.strip() for p in user_input.split("  ") if p.strip()]
            st.session_state.out = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
        except:
            st.error("Error!")

# Result & Share
if st.session_state.out:
    st.markdown(f'<div class="result-box">{st.session_state.out}</div>', unsafe_allow_html=True)
    # This acts as the "Share" button - it won't disappear when clicked
    st.download_button("SHARE ✨", data=st.session_state.out, file_name="chemistry.txt")

if st.button("DESTROY CHEMISTRY"):
    st.session_state.out = ""
    st.rerun()

if os.path.exists("LPB.png"): st.image("LPB.png", width=600)

