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

# Mapping
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    .block-container {{ max-width: 100% !important; padding: 1rem !important; }}

    /* Input Styling */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 22px !important; font-weight: 900 !important;
        -webkit-text-fill-color: #B4A7D6 !important;
        border-radius: 15px !important;
    }}

    /* Giant Button Styling */
    div[data-testid="stButton"] > button {{
        width: 100% !important;
        background-color: #B4A7D6 !important; 
        border-radius: 25px !important;
        height: 100px !important; 
        border: none !important;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.15) !important;
        margin-bottom: 10px !important;
    }}

    div[data-testid="stButton"] > button p {{
        color: #FFD4E5 !important;
        font-size: 45px !important; 
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", Gadget, sans-serif !important;
    }}

    /* Result Box - The Mockup Look */
    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6 !important;
        padding: 20px;
        border-radius: 20px;
        border: 4px solid #B4A7D6;
        word-wrap: break-word;
        font-weight: 900;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 22px;
        margin-top: 10px;
        margin-bottom: 15px;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ENGINE ---
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
if kw: st.progress(min(len(kw) / 12.0, 1.0))

st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", use_container_width=True)
user_input = st.text_area("Message", height=150, key="chem", placeholder="YOUR MESSAGE")

# --- PLACEHOLDER FOR THE RESULT BOX & SHARE BUTTON ---
result_container = st.container()

# Bottom Action Buttons
kiss_btn = st.button("KISS")
tell_btn = st.button("TELL")

# Logic to fill the result box ABOVE the other buttons
if kw and user_input:
    a, b = get_stable_params(kw)
    res_text = ""
    
    if kiss_btn:
        encoded = [to_emoji((a * ord(c) + b) % U_MOD) for c in user_input]
        res_text = "  ".join(encoded)
    
    if tell_btn:
        try:
            a_inv = pow(a, -1, U_MOD)
            parts = [p.strip() for p in user_input.split("  ") if p.strip()]
            res_text = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
        except:
            st.error("Chemistry Error!")

    if res_text:
        with result_container:
            st.markdown(f'<div class="result-box">{res_text}</div>', unsafe_allow_html=True)
            # This is the giant SHARE button from your mockup
            if st.button("SHARE ✨"):
                st.write("Copied to clipboard!") # Placeholder for share action

# Destroy and Footer
if st.button("DESTROY CHEMISTRY"):
    for key in ["lips", "chem", "hint"]:
        if key in st.session_state: st.session_state[key] = ""
    st.rerun()

if os.path.exists("LPB.png"): st.image("LPB.png", use_container_width=True)
