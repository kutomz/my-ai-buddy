from gtts import gTTS
import io
import re
import requests
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. ตั้งค่าหน้าตาแอปหลัก
st.set_page_config(page_title="My AI Robot Boys", page_icon="🕸️", layout="wide")

# --- 🎨 เวทมนตร์ CSS ตกแต่งหน้าตา (Spider-Man Edition 🕸️) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Mitr:wght@300;400;500&display=swap');

    .stApp {
        background-color: #f0f2f6;
        font-family: 'Mitr', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    h1, h2, h3 {
        font-family: 'Bangers', cursive !important;
        letter-spacing: 2px;
    }

    .stHeading h1 {
        color: #E23636 !important; 
        text-shadow: 3px 3px 0px #2F3C7E; 
        font-size: 4rem !important;
    }

    [data-testid="stSidebar"] {
        background-color: #2F3C7E !important; 
        border-right: 5px solid #E23636;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: white !important;
    }
    
    /* 🛠️ แก้ปัญหาตัวหนังสือบนปุ่มล่องหน! */
    .stButton>button {
        border-radius: 20px !important;
        border: 2px solid #E23636 !important;
        background-color: white !important;
        transition: 0.3s;
    }
    /* บังคับตัวหนังสือในปุ่มให้เป็นสีน้ำเงินเข้มเสมอ */
    .stButton>button p {
        color: #2F3C7E !important; 
        font-weight: bold !important;
    }
    /* ตอนเอาเมาส์ไปวาง (Hover) ค่อยเปลี่ยนเป็นสีแดงและตัวหนังสือสีขาว */
    .stButton>button:hover {
        background-color: #E23636 !important;
        transform: scale(1.05);
    }
    .stButton>button:hover p {
        color: white !important;
    }

    /* 🛠️ บังคับให้ข้อความในแชทเป็นสีดำ! */
    .stChatMessage, .stChatMessage p, .stChatMessage div {
        color: #1A1A1B !important; 
    }

    .stChatMessage {
        border-radius: 25px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        border: 3px solid #1A1A1B !important; 
        box-shadow: 5px 5px 0px #ccc;
    }

    [data-testid="stChatMessageAssistant"] {
        background-color: #ffffff !important;
    }
    
    [data-testid="stChatMessageUser"] {
        background-color: #d1d9ff !important; 
    }

    .stChatInput {
        border: 3px solid #E23636 !important;
        border-radius: 30px !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. เริ่มต้นการเชื่อมต่อ AI
if "ai_client" not in st.session_state:
    st.session_state.ai_client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

def load_chat_from_sheet():
    try:
        response = requests.get(st.secrets["SHEET_API_URL"])
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception:
        return []
    return []

def save_chat_to_sheet(user, room, role, message):
    try:
        requests.post(st.secrets["SHEET_API_URL"], json={
            "action": "append",
            "user": user,
            "room": room,
            "role": role,
            "message": message
        })
    except Exception:
        pass

# --- 🔐 ระบบล็อกอินอย่างง่าย (อัปเกรดกัน F5 แล้วหลุด) ---
if "logged_in" not in st.session_state:
    if st.query_params.get("user") in ["sky", "daddy"]:
        st.session_state.logged_in = True
        st.session_state.user = st.query_params.get("user")
    else:
        st.markdown("<h2 style='text-align: center; color: #E23636; text-shadow: 2px 2px #2F3C7E;'>🕷️ เข้าสู่ฐานทัพลับ My AI Robot Boys 🕸️</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("ชื่อฮีโร่ (Username)")
            password = st.text_input("รหัสผ่านลับ (Password)", type="password")
            if st.button("ปล่อยใย เข้าสู่ระบบ! 🚀", use_container_width=True):
                if username.lower() == "sky" and password == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user = "sky"
                    st.query_params["user"] = "sky" 
                    st.rerun()
                elif username.lower() == "daddy" and password == "5678":
                    st.session_state.logged_in = True
                    st.session_state.user = "daddy"
                    st.query_params["user"] = "daddy" 
                    st.rerun()
                else:
                    st.error("❌ ชื่อฮีโร่หรือรหัสผ่านไม่ถูกต้อง ลองใหม่นะ!")
        st.stop()

# --- 🏠 เข้าสู่หน้า
