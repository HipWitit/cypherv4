import streamlit as st
import streamlit.components.v1 as components
import os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

st.set_page_config(page_title="Cyfer Pro", layout="centered")

# --- 1. ENGINE ---
raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 
EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

# Initialize memory to stop buttons from disappearing
if "result_text" not in st.session_state:
    st.session_state.result_text = ""

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

# --- 2. THE DESIGN ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 20px !important; font-weight: 900 !important;
        border-radius: 15px !important;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}

    /* ACTION BUTTONS (KISS, TELL, DESTROY) */
    div.stButton > button {{
        width: 100% !important; 
        height: 85px !important;
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 20px !important; 
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important;
        margin-bottom: 10px !important;
    }}
    div.stButton > button p {{
        font-size: 32px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", sans-serif !important;
    }}

    /* SHARE BUTTON (The Pink One) */
    div[data-testid="stButton"] button[key="sh_btn"] {{
        background-color: #FFD4E5 !important;
        box-shadow: 0px 6px 0px #e0b8c8 !important;
    }}
    div[data-testid="stButton"] button[key="sh_btn"] p {{
        color: #B4A7D6 !important;
    }}

    /* Result Box */
    .res-box {{
        background-color: #FEE2E9; color: #B4A7D6; padding: 20px;
        border-radius: 20px; border: 4px solid #B4A7D6;
        margin-bottom: 15px; text-align: center;
        font-family: monospace; font-size: 20px; font-weight: 900;
        word-break: break-all;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png", width='stretch')
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png", width='stretch')

# Move the Destroy button to the very top or bottom? Let's put it right after images for now
if st.button("DESTROY CHEMISTRY", key="dest_top"):
    for k in ["lips", "chem", "hint"]: 
        if k in st.session_state: st.session_state[k] = ""
    st.session_state.result_text = ""
    st.rerun()

kw_input = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", width='stretch')
msg_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# --- 4. ENGINE LOGIC ---
col1, col2 = st.columns(2) # Side by side for KISS/TELL to save space

if st.button("KISS"):
    if kw_input and msg_input:
        a, b = get_params(kw_input)
        st.session_state.result_text = "  ".join([to_emoji((a * ord(c) + b) % U_MOD) for c in msg_input])

if st.button("TELL"):
    if kw_input and msg_input:
        try:
            a, b = get_params(kw_input)
            a_inv = pow(a, -1, U_MOD)
            parts = [p.strip() for p in msg_input.split("  ") if p.strip()]
            st.session_state.result_text = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
        except:
            st.error("Error! Check your emojis.")

# --- 5. RESULT & SHARE ---
if st.session_state.result_text:
    st.markdown(f'<div class="res-box">{st.session_state.result_text}</div>', unsafe_allow_html=True)
    
    # SHARE BUTTON triggers the JS bridge
    if st.button("SHARE ✨", key="sh_btn"):
        components.html(f"""
            <script>
            if (navigator.share) {{
                navigator.share({{ title: 'Cyfer', text: '{st.session_state.result_text}' }});
            }} else {{
                navigator.clipboard.writeText('{st.session_state.result_text}');
                alert('Copied!');
            }}
            </script>
        """, height=0)

if os.path.exists("LPB.png"): st.image("LPB.png", width='stretch')
