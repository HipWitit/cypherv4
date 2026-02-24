import streamlit as st
import re, random, hashlib, math, base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Cyfer Pro: Unicode", layout="centered")
U_MOD = 1114112 
PEPPER = str(st.secrets.get("MY_SECRET_PEPPER", "global_2026"))
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color: #FEE2E9 !important; color: #B4A7D6 !important; 
        border: 2px solid #B4A7D6 !important; font-family: "Courier New", Courier, monospace !important;
        font-size: 18px !important; font-weight: bold !important;
    }}
    div.stButton > button {{
        background-color: #B4A7D6 !important; color: #FFD4E5 !important;
        border-radius: 15px !important; min-height: 80px !important; width: 100%;
        font-size: 30px !important; font-weight: 800 !important; border: none !important;
    }}
    .result-box {{
        background-color: #FEE2E9; color: #B4A7D6; padding: 15px;
        border-radius: 10px; border: 2px solid #B4A7D6; word-wrap: break-word; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE ---
def get_params(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"uni_v5", iterations=100000, backend=default_backend())
    seed = int.from_bytes(hashlib.sha256(kdf.derive((kw + PEPPER).encode())).digest(), 'big')
    rng = random.Random(seed)
    a = rng.randint(3, 100000)
    while math.gcd(a, U_MOD) != 1: a += 1
    return a, rng.randint(1000, 900000)

def num_to_emoji(n): return "".join(EMOJI_MAP[d] for d in str(n))
def emoji_to_num(s): return int("".join(REV_MAP.get(c, c) for c in s))

# --- 3. UI ---
kw = st.text_input("Key", type="password", placeholder="SECRET KEY")

if kw:
    strength = min(len(kw) / 12.0, 1.0)
    st.write(f"🧪 **CHEMISTRY LEVEL:** {int(strength*100)}%")
    st.progress(strength)

msg = st.text_area("Message", placeholder="Emojis allowed! 🦄♾️🌈")

col1, col2 = st.columns(2)
if kw and msg:
    a, b = get_params(kw)
    if col1.button("KISS"):
        # Affine: (a*x + b) % MOD
        coded = [num_to_emoji((a * ord(c) + b) % U_MOD) for c in msg]
        st.markdown(f'<div class="result-box">{" 🌸 ".自行(coded)}</div>', unsafe_allow_html=True)
        # Note: '🌸' acts as a separator between character clusters
        
    if col2.button("TELL"):
        try:
            a_inv = pow(a, -1, U_MOD)
            parts = msg.strip().split(" 🌸 ")
            # Reverse: a_inv * (y - b) % MOD
            decoded = "".join(chr((a_inv * (emoji_to_num(p) - b)) % U_MOD) for p in parts)
            st.success(f"Whisper: {decoded}")
        except:
            st.error("Chemistry Error! Make sure you used the right key.")
