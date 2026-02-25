import streamlit as st

# --- 1. CONFIG & PWA HEADERS ---
st.set_page_config(page_title="Cypher Lite", layout="centered")

st.markdown(f"""
    <link rel="manifest" href="https://raw.githubusercontent.com/HipWitit/cypher-v4/main/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#B4A7D6">
""", unsafe_allow_html=True)

import re
import os
import secrets
import hashlib
import math
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 2. CRYPTO-STRENGTH ENGINE ---
raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper).encode()
U_MOD = 256 
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

    /* Styling for the Credit Text at the bottom */
    .credit-text {{
        color: #B4A7D6;
        font-family: "Courier New", monospace !important;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        font-size: 16px;
    }}
    </style>
    """, unsafe_allow_html=True)

EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

def to_emoji(val): return "".join(EMOJI_MAP.get(d, d) for d in f"{val:03}")
def from_emoji(s):
    res = "".join(REV_MAP[char] for char in s if char in REV_MAP)
    return int(res) if res else 0

def get_keys_and_perms(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=64, salt=b"csprng_v3", iterations=100000, backend=default_backend())
    master_key = kdf.derive(kw.encode() + PEPPER)
    rounds_params = []
    for i in range(ROUNDS):
        h = hashlib.sha256(master_key + i.to_bytes(4, 'big')).digest()
        a = (int.from_bytes(h[:4], 'big') % 120) * 2 + 1 
        b = int.from_bytes(h[4:8], 'big') % 256
        p_list = list(range(256))
        seed = int.from_bytes(h[8:16], 'big')
        import random
        r = random.Random(seed)
        r.shuffle(p_list)
        rounds_params.append({'a': a, 'b': b, 'p': p_list, 'inv_p': [p_list.index(j) for j in range(256)]})
    return rounds_params

def clear_everything():
    for k in ["lips", "chem", "hint"]:
        if k in st.session_state:
            st.session_state[k] = ""

# --- 3. UI LAYOUT ---
st.title("Cypher Lite 🧪")

if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

output_placeholder = st.empty()
kiss_btn, tell_btn = st.button("KISS"), st.button("TELL")
st.button("DESTROY CHEMISTRY", on_click=clear_everything)

# --- FOOTER SECTION (LPB & CREDIT) ---
st.write("---") # Adds a subtle divider line
if os.path.exists("LPB.png"): 
    st.image("LPB.png")
st.markdown('<p class="credit-text">CREATED BY LOVE POTION BOTTLE</p>', unsafe_allow_html=True)

# --- 4. PROCESSING ---
if kw and (kiss_btn or tell_btn):
    params = get_keys_and_perms(kw)
    if kiss_btn:
        data = user_input.encode('utf-8')
        nonce_bytes = [secrets.randbelow(256) for _ in range(4)]
        prev = int.from_bytes(hashlib.sha256(bytes(nonce_bytes)).digest()[:1], 'big')
        res_list = [to_emoji(b) for b in nonce_bytes]
        for byte in data:
            current = byte ^ prev
            for r in range(ROUNDS):
                current = params[r]['p'][current]
                current = (params[r]['a'] * current + params[r]['b']) % 256
            res_list.append(to_emoji(current))
            prev = current
        res = " ".join(res_list)
        with output_placeholder.container():
            st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
            components.html(f"""<button onclick="navigator.share({{title:'Secret',text:`{res}\\n\\nHint: {hint_text}`}})" style="background-color:#B4A7D6; color:#FFD4E5; font-weight:bold; border-radius:15px; min-height:80px; width:100%; cursor:pointer; font-size: 28px; border:none; text-transform:uppercase;">SHARE ✨</button>""", height=100)

    if tell_btn:
        try:
            parts = [from_emoji(p) for p in user_input.split(" ") if p.strip()]
            if len(parts) < 5: raise ValueError("Message too short")
            nonce_bytes = parts[:4]
            ciphertext_payload = parts[4:]
            prev = int.from_bytes(hashlib.sha256(bytes(nonce_bytes)).digest()[:1], 'big')
            decoded_bytes = []
            for current_cipher in ciphertext_payload:
                temp = current_cipher
                for r in reversed(range(ROUNDS)):
                    a_inv = pow(params[r]['a'], -1, 256)
                    temp = (a_inv * (temp - params[r]['b'])) % 256
                    temp = params[r]['inv_p'][temp]
                original_byte = temp ^ prev
                decoded_bytes.append(original_byte)
                prev = current_cipher
            decoded_msg = bytes(decoded_bytes).decode('utf-8')
            output_placeholder.markdown(f'<div class="whisper-text">Cypher Whispers: {decoded_msg}</div>', unsafe_allow_html=True)
        except Exception:
            st.error("Chemistry Error! Check Key or Hint.")
