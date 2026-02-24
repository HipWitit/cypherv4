import streamlit as st
import re
import os
import secrets
import hashlib
import math
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & STYLING (Sacred Layout) ---
st.set_page_config(page_title="Cyfer Pro: Secret Language", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper).encode()
U_MOD = 256 # Operating on bytes now
ROUNDS = 3

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

# --- 2. CRYPTO-STRENGTH ENGINE ---
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

def to_emoji(val): return "".join(EMOJI_MAP.get(d, d) for d in f"{val:03}")
def from_emoji(s):
    res = "".join(REV_MAP[char] for char in s if char in REV_MAP)
    return int(res) if res else 0

def get_keys_and_perms(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=64, salt=b"csprng_v1", iterations=100000, backend=default_backend())
    master_key = kdf.derive(kw.encode() + PEPPER)
    
    # Derive round parameters (a, b for each round)
    rounds_params = []
    for i in range(ROUNDS):
        h = hashlib.sha256(master_key + i.to_bytes(4, 'big')).digest()
        a = (int.from_bytes(h[:4], 'big') % 120) * 2 + 1 # Ensure odd for MOD 256
        b = int.from_bytes(h[4:8], 'big') % 256
        
        # Create round permutation
        p_list = list(range(256))
        seed = int.from_bytes(h[8:16], 'big')
        import random
        r = random.Random(seed) # Deterministic shuffle per round
        r.shuffle(p_list)
        rounds_params.append({'a': a, 'b': b, 'p': p_list, 'inv_p': [p_list.index(j) for j in range(256)]})
    
    # Initialization Vector (derived from key for stability)
    iv = int.from_bytes(hashlib.sha256(master_key + b"iv").digest()[:1], 'big')
    return rounds_params, iv

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
    params, iv = get_keys_and_perms(kw)
    
    if kiss_btn:
        data = user_input.encode('utf-8')
        prev = iv
        res_list = []
        
        for byte in data:
            # Position-dependent mixing (XOR)
            current = byte ^ prev
            
            # Multiple Rounds of Permute + Affine
            for r in range(ROUNDS):
                # 1. Permute
                current = params[r]['p'][current]
                # 2. Affine
                current = (params[r]['a'] * current + params[r]['b']) % 256
            
            res_list.append(to_emoji(current))
            prev = current # Feed-forward for next byte
        
        res = " ".join(res_list)
        with output_placeholder.container():
            st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
            components.html(f"""<button onclick="navigator.share({{title:'Secret',text:`{res}\\n\\nHint: {hint_text}`}})" style="background-color:#B4A7D6; color:#FFD4E5; font-weight:bold; border-radius:15px; min-height:80px; width:100%; cursor:pointer; font-size: 28px; border:none; text-transform:uppercase;">SHARE ✨</button>""", height=100)

    if tell_btn:
        try:
            parts = [from_emoji(p) for p in user_input.split(" ") if p.strip()]
            prev = iv
            decoded_bytes = []
            
            for current_cipher in parts:
                temp = current_cipher
                # Reverse Rounds
                for r in reversed(range(ROUNDS)):
                    # 1. Reverse Affine
                    a_inv = pow(params[r]['a'], -1, 256)
                    temp = (a_inv * (temp - params[r]['b'])) % 256
                    # 2. Reverse Permute
                    temp = params[r]['inv_p'][temp]
                
                # Reverse XOR
                original_byte = temp ^ prev
                decoded_bytes.append(original_byte)
                prev = current_cipher
            
            decoded_msg = bytes(decoded_bytes).decode('utf-8')
            output_placeholder.markdown(f'<div class="whisper-text">Cypher Whispers: {decoded_msg}</div>', unsafe_allow_html=True)
        except:
            st.error("Chemistry Error! Key or formatting mismatch.")
