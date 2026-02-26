import streamlit as st
import os
import secrets
import hashlib
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import traceback

# --- 1. CONFIG & PWA HEADERS ---
st.set_page_config(page_title="Cypher Lite", layout="centered")

st.markdown(f"""
    <link rel="manifest" href="https://raw.githubusercontent.com/HipWitit/cypherv4/main/manifest.json?v=1.1">
    <link rel="icon" type="image/png" href="https://raw.githubusercontent.com/HipWitit/cypherv4/main/appicon.png">
    <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/HipWitit/cypherv4/main/appicon.png">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#B4A7D6">
""", unsafe_allow_html=True)

# --- 2. CRYPTO-STRENGTH ENGINE ---
# DEFENSIVE: Ensure PEPPER is consistent. 
# Check your Streamlit Secrets tab in the dashboard!
raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper).encode()
ROUNDS = 3

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }}
    .stButton > button {{
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 15px !important;
        min-height: 100px !important; 
        width: 100% !important;
        font-size: 38px !important;
        font-weight: 800 !important;
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
    .credit-text {{ color: #B4A7D6; font-family: "Courier New", monospace !important; text-align: center; font-size: 16px; }}
    </style>
    """, unsafe_allow_html=True)

EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

def to_emoji(val): return "".join(EMOJI_MAP.get(d, d) for d in f"{val:03}")

def from_emoji(s):
    digits = [REV_MAP[ch] for ch in s if ch in REV_MAP]
    if len(digits) != 3: return None
    return int("".join(digits))

def get_keys_and_perms(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=64, salt=b"csprng_v3", iterations=100000, backend=default_backend())
    master_key = kdf.derive(kw.encode() + PEPPER)
    rounds_params = []
    for i in range(ROUNDS):
        h = hashlib.sha256(master_key + i.to_bytes(4, 'big')).digest()
        # FIX 1: Defensive modular reduction for 'a'
        a = ((int.from_bytes(h[:4], 'big') % 120) * 2 + 1) % 256
        b = int.from_bytes(h[4:8], 'big') % 256
        p_list = list(range(256))
        import random
        r_gen = random.Random(int.from_bytes(h[8:16], 'big'))
        r_gen.shuffle(p_list)
        # FIX 2: O(N) inverse permutation construction
        inv_p = [0] * 256
        for idx, val in enumerate(p_list):
            inv_p[val] = idx
        rounds_params.append({'a': a, 'b': b, 'p': p_list, 'inv_p': inv_p})
    return rounds_params

def clear_everything():
    for k in ["lips", "chem", "hint"]:
        if k in st.session_state: st.session_state[k] = ""

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

output_placeholder = st.empty()
kiss_btn, tell_btn = st.button("KISS"), st.button("TELL")
st.button("DESTROY CHEMISTRY", on_click=clear_everything)

st.write("---") 
st.markdown('<p class="credit-text">CREATED BY LILPEACHBAT</p>', unsafe_allow_html=True)

# --- 4. PROCESSING ---
if kw and (kiss_btn or tell_btn):
    params = get_keys_and_perms(kw)
    
    if kiss_btn:
        data = user_input.encode('utf-8')
        tag = hashlib.sha256(data).digest()[:4]
        payload = data + tag
        nonce_bytes = [secrets.randbelow(256) for _ in range(4)]
        prev = int.from_bytes(hashlib.sha256(bytes(nonce_bytes)).digest()[:1], 'big')
        res_list = [to_emoji(b) for b in nonce_bytes]
        
        for byte in payload:
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
            # Aggressive split to ignore trailing text (Hints, etc)
            parts = []
            for chunk in user_input.split():
                val = from_emoji(chunk)
                if val is not None: parts.append(val)
                else: break # Stop if we hit non-emoji text (like "Hint:...")

            if len(parts) < 9: raise ValueError(f"Incomplete Message (Expected 9+ blocks, got {len(parts)})")
            
            nonce_ints = parts[:4]
            ciphertext_payload = parts[4:]
            prev = int.from_bytes(hashlib.sha256(bytes(nonce_ints)).digest()[:1], 'big')
            
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
            
            final_data = bytes(decoded_bytes[:-4])
            received_tag = bytes(decoded_bytes[-4:])
            computed_tag = hashlib.sha256(final_data).digest()[:4]
            
            if computed_tag != received_tag:
                st.error("Integrity Mismatch: Key is wrong or message was corrupted.")
            else:
                output_placeholder.markdown(f'<div class="whisper-text">Cypher Whispers: {final_data.decode("utf-8")}</div>', unsafe_allow_html=True)
        
        except Exception as e:
            # FIX: The "Anti-Mystery" Debugger
            st.error("Chemistry Unstable!")
            with st.expander("Show Diagnostic Trace"):
                st.code(traceback.format_exc())
