import streamlit as st
import streamlit.components.v1 as components
import os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

st.set_page_config(page_title="Cyfer Pro", layout="centered")

# --- ENGINE ---
raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

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

# --- STYLES ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    .stTextInput input, .stTextArea textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 20px !important; font-weight: 900 !important;
        border-radius: 15px !important;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}
    .result-box {{
        background-color: #FEE2E9; color: #B4A7D6; padding: 20px;
        border-radius: 20px; border: 4px solid #B4A7D6;
        word-wrap: break-word; font-weight: 900;
        font-family: "Courier New", monospace; font-size: 22px;
        margin-bottom: 15px; text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- UI ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png", width=600)
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png", width=600)

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", width=600)
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# --- ACTION BUTTONS (The Fixed Ones) ---
# We use a custom component to handle KISS/TELL/SHARE all at once
if kw and user_input:
    a, b = get_params(kw)
    
    # Process inputs for the buttons
    kiss_res = "  ".join([to_emoji((a * ord(c) + b) % U_MOD) for c in user_input])
    
    tell_res = ""
    try:
        a_inv = pow(a, -1, U_MOD)
        parts = [p.strip() for p in user_input.split("  ") if p.strip()]
        tell_res = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
    except:
        tell_res = "Chemistry Error!"

    # The HTML/JS Bridge
    components.html(f"""
        <style>
            .btn {{
                width: 100%; height: 80px; margin-bottom: 15px;
                border-radius: 20px; border: none; font-weight: 900;
                font-family: "Arial Black", sans-serif; font-size: 28px;
                text-transform: uppercase; cursor: pointer;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0px 6px 0px #9d8dbd; transition: 0.1s;
            }}
            .purple {{ background-color: #B4A7D6; color: #FFD4E5; }}
            .pink {{ background-color: #FFD4E5; color: #B4A7D6; box-shadow: 0px 6px 0px #e0b8c8; }}
            .btn:active {{ transform: translateY(4px); box-shadow: 0px 2px 0px #9d8dbd; }}
            .res {{ display:none; }}
        </style>

        <button class="btn purple" onclick="show('kiss')">KISS</button>
        <button class="btn purple" onclick="show('tell')">TELL</button>
        
        <div id="kiss_box" class="res"><div style='background:#FEE2E9; color:#B4A7D6; padding:20px; border-radius:20px; border:4px solid #B4A7D6; margin-bottom:15px; text-align:center; font-family:monospace; font-weight:900;'>{kiss_res}</div><button class="btn pink" onclick="share('{kiss_res}')">SHARE ✨</button></div>
        <div id="tell_box" class="res"><div style='background:#FEE2E9; color:#B4A7D6; padding:20px; border-radius:20px; border:4px solid #B4A7D6; margin-bottom:15px; text-align:center; font-family:monospace; font-weight:900;'>{tell_res}</div><button class="btn pink" onclick="share('{tell_res}')">SHARE ✨</button></div>

        <script>
            function show(id) {{
                document.getElementById('kiss_box').style.display = 'none';
                document.getElementById('tell_box').style.display = 'none';
                document.getElementById(id + '_box').style.display = 'block';
            }}
            function share(txt) {{
                if (navigator.share) {{
                    navigator.share({{ title: 'Cyfer', text: txt }});
                }} else {{
                    navigator.clipboard.writeText(txt);
                    alert('Copied!');
                }}
            }}
        </script>
    """, height=600)

if st.button("DESTROY CHEMISTRY"):
    for k in ["lips", "chem", "hint"]: st.session_state[k] = ""
    st.rerun()

if os.path.exists("LPB.png"): st.image("LPB.png", width=600)
