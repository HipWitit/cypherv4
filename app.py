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

    /* 1. Text Inputs - Fixed Color & Font */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 20px !important; 
        font-weight: 900 !important;
        border-radius: 15px !important;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}

    /* 2. BUTTON PROPORTIONS FIX */
    /* This ensures every button container takes up the full width */
    div[data-testid="stVerticalBlock"] > div {{
        width: 100% !important;
    }}

    /* The actual button styling */
    div.stButton > button {{
        width: 100% !important;
        height: 90px !important; /* Force a uniform height for all buttons */
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 10px 0px !important;
    }}

    /* Ensuring text doesn't cause the button to expand/contract */
    div.stButton > button p {{
        font-size: 32px !important; 
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", sans-serif !important;
        line-height: 1 !important;
        margin: 0 !important;
        white-space: nowrap !important; /* Keep text on one line */
    }}

    /* SHARE BUTTON: Pink Background, Purple Text */
    div.stButton > button[key="share_btn"] {{
        background-color: #FFD4E5 !important;
        box-shadow: 0px 6px 0px #e0b8c8 !important;
    }}
    div.stButton > button[key="share_btn"] p {{
        color: #B4A7D6 !important;
    }}

    /* Scale down font for long button text to keep proportions identical */
    div.stButton:last-of-type > button p {{
        font-size: 22px !important;
    }}

    /* 3. Result Box */
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

# --- 3. UI LAYOUT ---
# Updated width logic to match your logs
def show_img(name):
    if os.path.exists(name): st.image(name, width=600) # 'stretch' is the new standard but width works best for stability

show_img("CYPHER.png")
show_img("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

show_img("Kiss Chemistry.png")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# Placeholder for Result area
result_spot = st.container()

# Action Buttons
kiss_btn = st.button("KISS")
tell_btn = st.button("TELL")

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
            st.button("SHARE ✨", key="share_btn")

destroy_btn = st.button("DESTROY CHEMISTRY")

if destroy_btn:
    for key in ["lips", "chem", "hint"]:
        if key in st.session_state: st.session_state[key] = ""
    st.rerun()

show_img("LPB.png")
