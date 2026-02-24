import streamlit as st
import os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & REFINED CSS ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 

EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    .block-container {{ max-width: 100% !important; padding: 1rem !important; }}

    /* Text Boxes */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 20px !important; 
        font-weight: 900 !important;
        border-radius: 15px !important;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}

    /* THE BUTTON MASTER FIX */
    div[data-testid="stButton"] {{
        width: 100% !important;
        margin-bottom: 12px !important;
    }}

    div[data-testid="stButton"] > button {{
        width: 100% !important;
        height: 80px !important; /* Fixed height for consistent proportions */
        background-color: #B4A7D6 !important; 
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important; /* Thick "pop" shadow */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.1s ease;
    }}

    div[data-testid="stButton"] > button:active {{
        transform: translateY(4px);
        box-shadow: 0px 2px 0px #9d8dbd !important;
    }}

    div[data-testid="stButton"] > button p {{
        color: #FFD4E5 !important;
        font-size: 35px !important; 
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", sans-serif !important;
        margin: 0 !important;
        line-height: 1 !important;
    }}

    /* Specific scaling for the long text on Destroy button */
    div[data-testid="stVerticalBlock"] > div:nth-last-of-type(2) button p {{
        font-size: 22px !important;
    }}

    /* SHARE Button - Making it pop with a different shade */
    div.stButton > button[kind="secondary"] {{
        background-color: #FFD4E5 !important;
        box-shadow: 0px 6px 0px #e0b8c8 !important;
    }}
    div.stButton > button[kind="secondary"] p {{
        color: #B4A7D6 !important;
    }}

    /* Result Box */
    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6 !important;
        padding: 20px;
        border-radius: 20px;
        border: 4px solid #B4A7D6;
        word-wrap: break-word;
        font-weight: 900;
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
def from_emoji(s): return int("".join(REV_MAP.get(c, v) for v in [s] for c in s if c in REV_MAP)) # Fix for split logic

def get_params(kw):
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
st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", use_container_width=True)
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# Placeholder for Result area
result_spot = st.container()

kiss_btn = st.button("KISS")
tell_btn = st.button("TELL")
destroy_btn = st.button("DESTROY CHEMISTRY")

if kw and user_input:
    a, b = get_params(kw)
    output = ""
    
    if kiss_btn:
        encoded = [to_emoji((a * ord(c) + b) % U_MOD) for c in user_input]
        output = "  ".join(encoded)
    
    if tell_btn:
        try:
            a_inv = pow(a, -1, U_MOD)
            parts = [p.strip() for p in user_input.split("  ") if p.strip()]
            output = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
        except:
            st.error("Error!")

    if output:
        with result_spot:
            st.markdown(f'<div class="result-box">{output}</div>', unsafe_allow_html=True)
            # kind="secondary" helps us style it differently in CSS
            st.button("SHARE ✨", key="share_btn", type="secondary")

if destroy_btn:
    for key in ["lips", "chem", "hint"]:
        if key in st.session_state: st.session_state[key] = ""
    st.rerun()

if os.path.exists("LPB.png"): st.image("LPB.png", use_container_width=True)
