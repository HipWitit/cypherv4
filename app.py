import streamlit as st
import re
import os
import random
import hashlib
import math
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Cyfer Pro: Secret Language", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    .main .block-container {{ padding-bottom: 150px !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}

    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    input::placeholder, textarea::placeholder {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }}

    .stProgress > div > div > div > div {{ background-color: #B4A7D6 !important; }}

    [data-testid="column"], [data-testid="stVerticalBlock"] > div {{ width: 100% !important; flex: 1 1 100% !important; }}
    .stButton, .stButton > button {{ width: 100% !important; display: block !important; }}

    div.stButton > button p {{
        font-size: 38px !important; 
        font-weight: 800 !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        text-align: center !important;
    }}

    div.stButton > button {{
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 15px !important;
        min-height: 100px !important; 
        border: none !important;
        text-transform: uppercase;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        margin-top: 15px !important;
    }}

    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button p {{ font-size: 24px !important; }}
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {{
        min-height: 70px !important;
        background-color: #D1C4E9 !important;
    }}

    .result-box {{
        background-color: #FEE2E9; color: #B4A7D6; padding: 15px;
        border-radius: 10px; font-family: "Courier New", monospace !important;
        border: 2px solid #B4A7D6; word-wrap: break-word;
        margin-top: 15px; font-weight: bold; text-align: center;
    }}

    .whisper-text {{
        color: #B4A7D6; font-family: "Courier New", monospace !important;
        font-weight: bold; font-size: 26px; margin-top: 20px;
        border-top: 2px dashed #B4A7D6; padding-top: 15px; text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE WITH PERMUTATION LAYER ---
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

def to_emoji(val): return "".join(EMOJI_MAP.get(d, d) for d in str(val))
def from_emoji(s):
    res = "".join(REV_MAP[char] for char in s if char in REV_MAP)
    return int(res) if res else 0

def get_crypto_tools(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"perm_affine_v1", iterations=100000, backend=default_backend())
    seed = int.from_bytes(hashlib.sha256(kdf.derive((kw + PEPPER).encode())).digest(), 'big')
    rng = random.Random(seed)
    
    # Affine Params
    a = rng.randint(3, 100000)
    while math.gcd(a, U_MOD) != 1: a += 1 
    b = rng.randint(1000, 900000)
    
    # Permutation Key (Used to "Shuffle" the specific character block)
    perm_seed = rng.getrandbits(64)
    return a, b, perm_seed

def apply_permutation(char_code, seed, inverse=False):
    # This acts as a Key-Derived S-Box for the local Unicode block
    block_size = 256
    block_id = char_code // block_size
    offset = char_code % block_size
    
    rng = random.Random(seed + block_id)
    p_map = list(range(block_size))
    rng.shuffle(p_map)
    
    if inverse:
        return (block_id * block_size) + p_map.index(offset)
    return (block_id * block_size) + p_map[offset]

def clear_everything():
    for k in ["lips", "chem", "hint"]: st.session_state[k] = ""

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

output_placeholder = st.empty()
kiss_btn, tell_btn = st.button("KISS"), st.button("TELL")
st.button("DESTROY CHEMISTRY", on_click=clear_everything)

# --- 4. PROCESSING ---
if kw and (kiss_btn or tell_btn):
    a, b, p_seed = get_crypto_tools(kw)
    
    if kiss_btn:
        res_list = []
        for c in user_input:
            # 1. Permutation Layer (S-Box)
            permuted = apply_permutation(ord(c), p_seed)
            # 2. Affine Layer
            transformed = (a * permuted + b) % U_MOD
            res_list.append(to_emoji(transformed))
        
        res = "  ".join(res_list)
        with output_placeholder.container():
            st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
            components.html(f"""<button onclick="navigator.share({{title:'Secret',text:`{res}\\n\\nHint: {hint_text}`}})" style="background-color:#B4A7D6; color:#FFD4E5; font-weight:bold; border-radius:15px; min-height:80px; width:100%; cursor:pointer; font-size: 28px; border:none; text-transform:uppercase;">SHARE ✨</button>""", height=100)

    if tell_btn:
        try:
            a_inv = pow(a, -1, U_MOD)
            clean_in = user_input.split("Hint:")[0].strip()
            parts = [p.strip() for p in clean_in.split("  ") if p.strip()]
            
            decoded = []
            for p in parts:
                # 1. Reverse Affine
                val = (a_inv * (from_emoji(p) - b)) % U_MOD
                # 2. Reverse Permutation
                original_ord = apply_permutation(val, p_seed, inverse=True)
                decoded.append(chr(original_ord))
                
            output_placeholder.markdown(f'<div class="whisper-text">Cypher Whispers: {"".join(decoded)}</div>', unsafe_allow_html=True)
        except:
            st.error("Chemistry Error!")
