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
    /* นำเข้าฟอนต์สไตล์การ์ตูนคอมมิค */
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Mitr:wght@300;400;500&display=swap');

    /* ตั้งค่าพื้นหลังและฟอนต์หลัก (ใช้ฟอนต์ Mitr ให้อ่านภาษาไทยง่ายขึ้น) */
    .stApp {
        background-color: #f0f2f6;
        font-family: 'Mitr', sans-serif;
    }

    /* ซ่อนเมนูรกๆ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ตกแต่ง Title และ Header ด้วยฟอนต์ Comic */
    h1, h2, h3 {
        font-family: 'Bangers', cursive !important;
        letter-spacing: 2px;
    }

    .stHeading h1 {
        color: #E23636 !important; /* สีแดง Spiderman */
        text-shadow: 3px 3px 0px #2F3C7E; /* เงาสีน้ำเงิน */
        font-size: 4rem !important;
    }

    /* ตกแต่ง Sidebar (เมนูด้านข้าง) */
    [data-testid="stSidebar"] {
        background-color: #2F3C7E !important; /* สีน้ำเงินเข้ม */
        border-right: 5px solid #E23636;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: white !important;
    }
    
    /* ตกแต่งปุ่มต่างๆ */
    .stButton>button {
        border-radius: 20px;
        border: 2px solid #E23636;
        background-color: white;
        color: #2F3C7E;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #E23636 !important;
        color: white !important;
        transform: scale(1.05);
    }

    /* ตกแต่งกล่องแชท (Chat Bubbles) ให้เหมือนคอมมิค */
    .stChatMessage {
        border-radius: 25px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        border: 3px solid #1A1A1B !important; /* ขอบดำหนาๆ สไตล์การ์ตูน */
        box-shadow: 5px 5px 0px #ccc;
    }

    /* แชทฝั่ง AI (RobotBoys) */
    [data-testid="stChatMessageAssistant"] {
        background-color: #ffffff !important;
    }
    
    /* แชทฝั่ง User (น้องสกาย) */
    [data-testid="stChatMessageUser"] {
        background-color: #d1d9ff !important; /* สีฟ้าอ่อน */
    }

    /* ปรับแต่งช่องกรอกข้อความด้านล่าง */
    .stChatInput {
        border: 3px solid #E23636 !important;
        border-radius: 30px !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. เริ่มต้นการเชื่อมต่อ AI
if "ai_client" not in st.session_state:
    st.session_state.ai_client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# ฟังก์ชันสำหรับดึงข้อมูลแชททั้งหมดจาก Google Sheet
def load_chat_from_sheet():
    try:
        response = requests.get(st.secrets["SHEET_API_URL"])
        if response.status_code == 200:
            return response.json().get("data", [])
    except Exception:
        return []
    return []

# ฟังก์ชันสำหรับบันทึกแชทลง Google Sheet
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
                elif username.lower()
