import streamlit as st
import streamlit.components.v1 as components
import os, random, hashlib, math
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "global_unicode_spice_2026"
PEPPER = str(raw_pepper)
U_MOD = 1114112 

EMOJI_MAP = {'0':'🦄','1':'🍼','2':'🩷','3':'🧸','4':'🎀','5':'🍓','6':'🌈','7':'🌸','8':'💕','9':'🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

if "result_output" not in st.session_state:
    st.session_state.result_output = ""

# --- 2. THE NUCLEAR CSS OPTION ---
# This forces every button to 90px height and full width, no matter what.
st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}
    .block-container {{ max-width: 100% !important; padding: 1rem !important; }}

    /* Force Inputs */
    .stTextInput input, .stTextArea textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 3px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 20px !important; font-weight: 900 !important;
        border-radius: 15px !important;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}

    /* THE BUTTON NUCLEAR FIX */
    /* Target every button in the app to be identical in size */
    button[kind="secondary"], button[kind="primary"] {{
        width: 100% !important;
        height: 90px !important;
        min-height: 90px !important;
        max-height: 90px !important;
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important;
        margin-bottom: 15px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Force text style inside all buttons */
    button p {{
        font-size: 32px !important; 
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: "Arial Black", sans-serif !important;
        color: #FFD4E5 !important;
    }}

    /* UNIQUE STYLE FOR SHARE (Pink) */
    /* We target this using the specific key later */
    div[data-testid="stButton"] button[key="share_btn_trigger"] {{
        background-color: #FFD4E5 !important;
        box-shadow: 0px 6px 0px #e0b8c8 !important;
    }}
    div[data-testid="stButton"] button[key="share_btn_trigger"] p {{
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
        margin-bottom: 20px;
        text-align: center;
        -webkit-text-fill-color: #B4A7D6 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE NATIVE SHARE COMPONENT ---
def trigger_share(text_to_share):
    # This creates a hidden JS bridge to open the native share menu
    components.html(
        f"""
        <script>
        const shareData = {{
            title: 'My Cyfer Message',
            text: '{text_to_share}'
        }};
        if (navigator.share) {{
            navigator.share(shareData).catch((err) => console.log(err));
        }} else {{
            navigator.clipboard.writeText('{text_to_share}');
            alert('Share menu not supported on this browser - Message Copied!');
        }}
        </script>
        """,
        height=0,
    )

# --- 4. ENGINE ---
def to_emoji(val): return "".join(EMOJI_MAP.get(d, d) for d in str(val))
def from_emoji(s):
    res = "".join(REV_MAP[char] for char in s if char in REV_MAP)
    return int(res) if res else 0

def get_params(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"uni_v5", iterations=100000, backend=default_backend())
    seed = int.from_bytes(hashlib.sha256(kdf.derive((kw
