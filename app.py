import streamlit as st
import streamlit.components.v1 as components
import os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. APP CONFIG ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 

EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

if "result_output" not in st.session_state:
    st.session_state.result_output = ""

# --- 2. THE CSS OVERRIDE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    .block-container {{ max-width: 100% !important; padding: 1rem !important; }}

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

    /* THE NUCLEAR BUTTON FIX: Uniform size for ALL buttons */
    button {{
        width: 100% !important;
        height: 90px !important;
        min-height: 90px !important;
        background-color: #B4A7D6 !important; 
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    button p {{
        color: #FFD4E5 !important;
        font-size: 28px !important; 
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", sans-serif !important;
    }}

    /* Specific scaling for DESTROY button text */
    button[data-testid="baseButton-secondary"]:last-child p {{
        font-size: 22px !important;
    }}

    /* PINK SHARE BUTTON OVERRIDE */
    /* We use a specific CSS selector to find the SHARE button */
    div[data-testid="stButton"] button:has(div p:contains("SHARE")) {{
        background-color: #FFD4E5 !important;
        box-shadow: 0px 6px 0px #e0b8c8 !important;
    }}
    div[data-testid="stButton"] button:has(div p:contains("SHARE")) p {{
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

# --- 3. NATIVE SHARE SCRIPT ---
def trigger_share(text):
    js_code = f"""
    <script>
    if (navigator.share) {{
        navigator.share({{
            title: 'Cyfer Message',
            text: '{text}'
        }}).catch(console.error);
    }} else {{
        navigator.clipboard.writeText('{text}');
        alert('Copied to clipboard!');
    }}
    </script>
    """
    components.html(js_code, height=0)

# --- 4. ENGINE ---
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

# --- 5. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png", width='stretch')
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png", width='stretch')

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", width='stretch')
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# Result Spot (above buttons)
res_container = st.container()

# Action Buttons
kiss = st.button("KISS")
tell = st.button("TELL")

if kw and user_input:
    a, b = get_params(kw)
    if kiss:
        encoded = [to_emoji((a * ord(c) + b) % U_MOD) for c in user_input]
        st.session_state.result_output = "  ".join(encoded)
    if tell:
        try:
            a_inv = pow(a, -1, U_MOD)
            parts = [p.strip() for p in user_input.split("  ") if p.strip()]
            st.session_state.result_output = "".join(chr((a_inv * (from_emoji(p) - b)) % U_MOD) for p in parts)
        except:
            st.error("Error!")

if st.session_state.result_output:
    with res_container:
        st.markdown(f'<div class="result-box">{st.session_state.result_output}</div>', unsafe_allow_html=True)
        if st.button("SHARE ✨"):
            trigger_share(st.session_state.result_output)

if st.button("DESTROY CHEMISTRY"):
    st.session_state.result_output = ""
    for k in ["lips", "chem", "hint"]: st.session_state[k] = ""
    st.rerun()

if os.path.exists("LPB.png"): st.image("LPB.png", width='stretch')
