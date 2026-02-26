import streamlit as st
import random
import pandas as pd
import math
import time
import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. SETTINGS & THEMING ---
st.set_page_config(page_title="Sorcery Sums", page_icon="🪄")

# Autorefresh for Leaderboard
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=30000, key="datarefresh")
except:
    pass

st.markdown(f"""
    <style>
    /* 1. Main Background */
    .stApp {{ background-color: #fde4f2; }}
    
    /* 2. Sidebar Background */
    [data-testid="stSidebar"] {{
        background-color: #ddfffc !important;
        border-right: 2px solid #c6c7ff;
    }}

    /* 3. PINK BACKGROUND FOR SUBJECT & GRADE SELECTION */
    /* This targets both the Selectbox and the Radio Button groups in the sidebar */
    div[data-testid="stSelectbox"], 
    div[role="radiogroup"] {{
        background-color: #ffdef2 !important;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #eecbff;
        margin-bottom: 20px;
    }}

    /* 4. RADIO BUTTONS: PERIWINKLE WHEN SELECTED */
    /* Outer circle of the radio button */
    div[role="radiogroup"] div[data-testid="stRadioButtonInternalDefaultCircle"] {{
        border-color: #7b7dbd !important;
        background-color: white !important;
    }}
    /* The periwinkle fill (#c6c7ff) when selected */
    div[role="radiogroup"] div[data-selection="true"] div {{
        background-color: #c6c7ff !important;
    }}

    /* 5. Hall of Wizards & Sidebar Text Color */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] .stTabs button,
    [data-testid="stSidebar"] [data-testid="stTable"] td,
    [data-testid="stSidebar"] [data-testid="stTable"] th,
    [data-testid="stSidebar"] label p {{
        color: #eecbff !important;
    }}
    
    /* Main interface styling */
    .question-container {{
        background-color: white; 
        padding: 30px; 
        border-radius: 20px; 
        border: 4px solid #c6c7ff; 
        text-align: center; 
        margin-bottom: 20px;
    }}
    
    .question-container h1, .question-container h3 {{
        color: #7b7dbd !important;
    }}

    /* Input Fields */
    div[data-testid="stTextArea"] textarea {{
        background-color: #b4a7d6 !important; 
        color: #d4ffea !important;           
        border-radius: 10px;
        border: 2px solid #7b7dbd;
    }}
    
    div[data-testid="stTextInput"] input {{
        background-color: #e6fff8 !important;
        color: #7b7dbd !important;
        border-radius: 10px;
    }}

    .stButton>button {{ 
        background-color: #c6c7ff; 
        color: white; 
        border-radius: 50px; 
        width: 100%; 
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SACRED STAR EFFECT ---
def pastel_star_effect():
    st.markdown("""
    <style>
    .star {
        position: fixed; width: 25px; height: 25px;
        clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
        animation: floatUp 2.5s ease-out forwards; z-index: 9999;
    }
    @keyframes floatUp {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-500px) rotate(360deg); opacity: 0; }
    }
    </style>
    <script>
    const colors = ["#ffd6ff","#caffbf","#fdffb6","#bdb2ff","#a0c4ff"];
    for (let i = 0; i < 30; i++) {
        let star = document.createElement("div");
        star.className = "star";
        star.style.left = Math.random() * window.innerWidth + "px";
        star.style.top = window.innerHeight + "px";
        star.style.background = colors[Math.floor(Math.random() * colors.length)];
        document.body.appendChild(star);
        setTimeout(() => star.remove(), 2500);
    }
    </script>
    """, unsafe_allow_html=True)

# --- 3. DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. LOGIN SCREEN ---
if "player_name" not in st.session_state:
    try:
        st.image("Sorcerer Login.png")
    except:
        st.write("✨ **Portal Opening...** ✨")
    name = st.text_input("Enter your name to begin your journey:")
    if st.button("Enter Realm"):
        if name:
            st.session_state.player_name = name
            st.rerun()
    st.stop()

# --- 5. MATH LOGIC BY UNIT & LEVEL ---
def generate_spell(unit, level):
    if "Algebra" in unit:
        difficulty = int(level) - 9
        x = random.randint(2, 10 * difficulty)
        a = random.randint(2, 5 * difficulty)
        b = random.randint(1, 20)
        c = (a * x) + b
        return f"Solve for x: {a}x + {b} = {c}", x

    elif "Quadratics" in unit:
        x = random.randint(1, 10)
        if level == "10":
            return f"Solve for x: x² = {x**2}", x
        else:
            x2 = random.randint(1, 5)
            b_val = -(x + x2)
            c_val = x * x2
            return f"Find one positive root: x² + ({b_val})x + {c_val} = 0", x

    elif "Functions" in unit:
        x = random.randint(2, 6)
        if level == "10":
            return f"f(x) = 3x + 5. Find f({x})", (3*x + 5)
        else:
            return f"f(x) = x² + 2. Find f({x})", (x**2 + 2)

    elif "Geometry" in unit:
        r = random.randint(2, 10)
        if level == "10":
            return f"Circle Radius = {r}. What is the Area? (Use 3.14)", round(3.14 * (r**2), 2)
        else:
            area = round(math.pi * (r**2), 2)
            return f"Circle Area = {area}. What is the radius r?", r
    
    return "Scroll not found", 0

# --- 6. SIDEBAR: LESSON SELECTION & LEADERBOARD ---
st.sidebar.title("📜 Choose Your Scroll")
unit_choice = st.sidebar.selectbox("Select Subject", ["Algebra", "Quadratics", "Functions", "Geometry"])
level_choice = st.sidebar.radio("Select Grade Level", ["10", "11", "12"])

# Reset question if unit/level changes
if ("last_unit" not in st.session_state or 
    st.session_state.last_unit != unit_choice or 
    st.session_state.last_level != level_choice):
    st.session_state.last_unit = unit_choice
    st.session_state.last_level = level_choice
    st.session_state.current_q, st.session_state.target_ans = generate_spell(unit_choice, level_choice)

# Hall of Wizards
st.sidebar.markdown("---")
st.sidebar.markdown("# 🏆 Hall of Wizards")
try:
    scores_df = conn.read(ttl=0)
    if not scores_df.empty:
        scores_df['Date'] = pd.to_datetime(scores_df['Date'])
        now = datetime.datetime.now()
        tab_w, tab_m, tab_y = st.sidebar.tabs(["Week", "Month", "Year"])
        with tab_w:
            w_data = scores_df[scores_df['Date'] >= (now - datetime.timedelta(days=7))]
            if not w_data.empty: st.table(w_data.groupby("Name")["Score"].sum().sort_values(ascending=False).astype(int))
        with tab_m:
            m_data = scores_df[scores_df['Date'].dt.month == now.month]
            if not m_data.empty: st.table(m_data.groupby("Name")["Score"].sum().sort_values(ascending=False).astype(int))
        with tab_y:
            y_data = scores_df[scores_df['Date'].dt.year == now.year]
            if not y_data.empty: st.table(y_data.groupby("Name")["Score"].sum().sort_values(ascending=False).astype(int))
except:
    st.sidebar.write("The scrolls are sleeping.")

# --- 7. MAIN INTERFACE ---
try:
    st.image("Sorcery Sums.png")
except:
    st.title("Sorcery Sums")

st.markdown(f"""
    <div class="question-container">
        <h3>Grade {level_choice} {unit_choice}</h3>
        <h1>{st.session_state.current_q}</h1>
    </div>
""", unsafe_allow_html=True)

st.text_area("Spellbook Scratchpad:", placeholder="Work out your equations here...", height=100, key="scratchpad")
user_answer_raw = st.text_input("Your Final Answer:", placeholder="Type number here...")

if st.button("🪄 Cast Spell!"):
    try:
        user_answer = float(user_answer_raw)
        if math.isclose(user_answer, st.session_state.target_ans, rel_tol=0.1):
            pastel_star_effect()
            st.markdown(f"""
                <div style="background-color: #ffffe3; border: 3px solid #b4a7d6; border-radius: 20px; padding: 20px; text-align: center; margin-top: 15px; margin-bottom: 15px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);">
                    <h2 style="color: #7b7dbd !important; margin: 0; font-size: 24px;">Correct! (｡◕‿◕｡)━☆ﾟ.*･｡ﾟ</h2>
                </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.5)
            try:
                df = conn.read(ttl=0)
                new_row = pd.DataFrame([{"Name": st.session_state.player_name, "Score": 50, "Date": datetime.datetime.now().strftime("%Y-%m-%d")}])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("✨ Score recorded! ✨")
                time.sleep(2.0)
            except:
                st.error("⚠️ Database Error")
            
            st.session_state.current_q, st.session_state.target_ans = generate_spell(unit_choice, level_choice)
            st.rerun()
        else:
            st.error("The magic failed! (╥﹏╥)")
    except ValueError:
        st.warning("🔮 Please enter a numeric answer!")
