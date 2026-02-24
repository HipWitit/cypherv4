import streamlit as st
import re
import os
import random
import hashlib
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Cyfer Pro", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "default_fallback_spice_2026"
PEPPER = str(raw_pepper)
MOD = 127 

# THE CSS FIX: Using your structure but forcing the sizes/colors
st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}

    /* Inputs */
    .stTextInput input, .stTextArea textarea {{
        background-color: #FEE2E9 !important;
        color: #B4A7D6 !important; 
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }}

    /* ACTION BUTTONS (KISS, TELL) */
    div.stButton > button {{
        width: 100% !important;
        min-height: 95px !important;
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #9d8dbd !important;
        margin-top: 15px !important;
    }}

    div.stButton > button p {{
        font-size: 34px !important; 
        font-weight: 800 !important;
        text-transform: uppercase !important;
    }}

    /* RESULT BOX */
    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #B4A7D6;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        font-family: monospace;
        text-align: center;
        word-break: break-all;
    }}

    /* DESTROY BUTTON (The bottom one) */
    div.stButton:last-of-type > button {{
        min-height: 70px !important;
        background-color: #D1C4E9 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE (Your Working Code) ---
EMOJI_MAP = {'1': '🦄', '2': '🍼', '3': '🩷', '4': '🧸', '5': '🎀', '6': '🍓', '7': '🌈', '8': '🌸', '9': '💕', '0': '🫐'}

def get_char_coord(char):
    val = ord(char) % MOD
    return (val, (val * 7) % MOD)

def get_fernet_sbox(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"v4", iterations=100000, backend=default_backend())
    derived = kdf.derive((kw + PEPPER).encode())
    seed = int.from_bytes(hashlib.sha256(derived).digest(), 'big')
    rng = random.Random(seed)
    sbox = list(range(MOD))
    rng.shuffle(sbox)
    return sbox, [sbox.index(i) for i in range(MOD)]

def get_matrix_elements(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=4, salt=b"m_v4", iterations=100000, backend=default_backend())
    a, b, c, d = list(kdf.derive((kw + PEPPER).encode()))
    return (a % 100 + 2, b % 100 + 1, c % 100 + 1, d % 100 + 2)

def modInverse(n, m=MOD):
    for x in range(1, m):
        if (((n % m) * (x % m)) % m == 1): return x
    return None

def apply_sweet_parity(val_str):
    def replacer(match):
        digit = match.group(2)
        return ('🍭' if int(digit) % 2 == 0 else '🍬') + digit
    return re.sub(r'(-)(\d)', replacer, val_str)

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png", width='stretch')
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png", width='stretch')

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png", width='stretch')
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

# We use your placeholder method
output_placeholder = st.empty()

kiss_btn = st.button("KISS")
tell_btn = st.button("TELL")

# --- 4. PROCESSING ---
if kw and (kiss_btn or tell_btn):
    a_mat, b_mat, c_mat, d_mat = get_matrix_elements(kw)
    det = (a_mat * d_mat - b_mat * c_mat) % MOD
    det_inv = modInverse(det)
    sbox, inv_sbox = get_fernet_sbox(kw)
    
    if det_inv:
        res_text = ""
        if kiss_btn:
            points = []
            for char in user_input:
                x_r, y_r = get_char_coord(char)
                x, y = sbox[x_r], sbox[y_r]
                nx, ny = (a_mat*x + b_mat*y) % MOD, (c_mat*x + d_mat*y) % MOD
                points.append((nx, ny))
            
            if points:
                def e_m(v): return "".join(EMOJI_MAP.get(d, d) for d in apply_sweet_parity(str(v)))
                hx = e_m(points[0][0])
                hy = e_m(points[0][1])
                header = f"{hx[::-1]},{hy[::-1]}"
                
                m_list = []
                for i in range(len(points)-1):
                    dx_v, dy_v = points[i+1][0]-points[i][0], points[i+1][1]-points[i][1]
                    dx, dy = e_m(dx_v), e_m(dy_v)
                    m_list.append(f"({dx[::-1]},{dy[::-1]})" if (i+1)%2==0 else f"({dx},{dy})")
                res_text = f"{header} | MOVES: {' '.join(m_list)}"

        if tell_btn:
            try:
                clean_in = user_input.split("Hint:")[0].strip()
                h_p, m_p = clean_in.split("|")
                rev_map = {v: k for k, v in EMOJI_MAP.items()}
                def e_to_int(s):
                    s = "".join(rev_map.get(ch, ch) for ch in s)
                    return int(s.replace('🍭', '-').replace('🍬', '-'))

                hx_e, hy_e = h_p.strip().split(",")
                cx, cy = e_to_int(hx_e[::-1]), e_to_int(hy_e[::-1])
                
                inv_a, inv_b = (d_mat * det_inv) % MOD, (-b_mat * det_inv) % MOD
                inv_c, inv_d = (-c_mat * det_inv) % MOD, (a_mat * det_inv) % MOD
                
                def resolve(x_val, y_val):
                    ux_s, uy_s = (inv_a * x_val + inv_b * y_val) % MOD, (inv_c * x_val + inv_d * y_val) % MOD
                    return chr(inv_sbox[ux_s])

                decoded = [resolve(cx, cy)]
                moves = re.findall(r"\(([^)]+)\)", m_p)
                for i, m in enumerate(moves):
                    dx_e, dy_e = m.split(",")
                    dx, dy = (e_to_int(dx_e[::-1]), e_to_int(dy_e[::-1])) if (i+1)%2==0 else (e_to_int(dx_e), e_to_int(dy_e))
                    cx, cy = cx + dx, cy + dy
                    decoded.append(resolve(cx, cy))
                res_text = "".join(decoded)
            except:
                res_text = "Chemistry Error!"

        with output_placeholder.container():
            st.markdown(f'<div class="result-box">{res_text}</div>', unsafe_allow_html=True)
            # PINK SHARE BUTTON using the method that worked in your version
            components.html(f"""
                <button onclick="navigator.share({{title:'Secret',text:`{res_text}\\n\\nHint: {hint_text}`}})" 
                style="background-color:#FFD4E5; color:#B4A7D6; font-weight:bold; border-radius:20px; 
                min-height:90px; width:100%; cursor:pointer; font-size: 30px; border:none; 
                text-transform:uppercase; box-shadow: 0px 4px 12px rgba(0,0,0,0.15);">
                SHARE ✨</button>
            """, height=120)

# --- 5. BOTTOM SECTION ---
def clear():
    for k in ["lips", "chem", "hint"]: st.session_state[k] = ""
st.button("DESTROY CHEMISTRY", on_click=clear)

if os.path.exists("LPB.png"): st.image("LPB.png", width='stretch')
