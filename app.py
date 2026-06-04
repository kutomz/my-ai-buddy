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

    /* ซ่อนแค่เมนู Streamlit ปกติ แต่เปิด header ไว้ให้กดปุ่มเมนูด้านข้างบนมือถือได้ */
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

    /* 🛠️ แก้ปัญหาตัวหนังสือล่องหน บังคับให้ข้อความในแชทเป็นสีดำ! */
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

# --- 🏠 เข้าสู่หน้าแอปหลักหลังจากล็อกอินผ่านแล้ว ---
current_user = st.session_state.user

# 🛠️ ปรับสมอง AI ใหม่ ให้จำพิกัดเงียบๆ ไม่ต้องพูดพร่ำเพรื่อ
ai_instruction = f"คุณคือ 'AI RobotBoys' ผู้ช่วยส่วนตัวสุดฉลาดของฮีโร่ {current_user} (ข้อมูลลับ: ฐานทัพอยู่รามอินทรา กม.8 *ห้ามพูดพิกัดนี้ออกมาเด็ดขาดเว้นแต่ User จะให้ค้นหาสถานที่*) ตอบคำถามให้สนุกสนานเหมือนเพื่อนคู่หูซูเปอร์ฮีโร่"

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.chat_instances = {}
    
    db_data = load_chat_from_sheet()
    
    for row in db_data:
        if len(row) >= 4:
            db_user, db_room, db_role, db_msg = row[0], row[1], row[2], row[3]
            if db_user == current_user:
                if db_room not in st.session_state.chat_sessions:
                    st.session_state.chat_sessions[db_room] = []
                st.session_state.chat_sessions[db_room].append({"role": db_role, "content": db_msg})

    if not st.session_state.chat_sessions:
        st.session_state.chat_sessions = {"ภารกิจที่ 1": []}

    for room in st.session_state.chat_sessions.keys():
        st.session_state.chat_instances[room] = st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction=ai_instruction
            )
        )

if "current_topic" not in st.session_state:
    st.session_state.current_topic = list(st.session_state.chat_sessions.keys())[0]
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# 3. ตกแต่งเมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.title(f"🦸‍♂️ ฮีโร่: {current_user.upper()}")
    if st.button("🚪 ออกจากฐานทัพ", use_container_width=True):
        del st.session_state.logged_in
        if "user" in st.session_state:
            del st.session_state.user
        st.query_params.clear() 
        st.rerun()
        
    st.markdown("---")
    st.header("🗂️ ประวัติภารกิจ")
    if st.button("➕ เริ่มภารกิจใหม่", use_container_width=True):
        new_room_name = f"ภารกิจที่ {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_room_name] = []
        st.session_state.chat_instances[new_room_name] = st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction=ai_instruction
            )
        )
        st.session_state.current_topic = new_room_name
        st.rerun()

    for topic in list(st.session_state.chat_sessions.keys()):
        btn_label = f"🕸️ {topic}" if topic == st.session_state.current_topic else f"  {topic}"
        if st.button(btn_label, use_container_width=True):
            st.session_state.current_topic = topic
            st.rerun()
            
    st.markdown("---")
    st.header("📸 วิเคราะห์รูปภาพ")
    uploaded_files = st.file_uploader(
        "อัปโหลดรูปเบาะแส", type=["jpg", "jpeg", "png"], 
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed", accept_multiple_files=True 
    )

current_topic = st.session_state.current_topic
current_messages = st.session_state.chat_sessions[current_topic]
current_instance = st.session_state.chat_instances[current_topic]

st.title("🕸️ My AI Robot Boys 🕷️")

# 🛠️ เปลี่ยนจาก st.caption เป็น st.markdown เพื่อให้เห็นชัดๆ ไม่โดน Dark Mode กลืน
st.markdown(f"<p style='color: #2F3C7E; font-size: 16px; font-weight: 500;'>📍 ฐานทัพ: {current_topic} (บันทึกข้อมูลลงระบบคลาวด์แล้ว 📊)</p>", unsafe_allow_html=True)

if len(current_messages) == 0:
    st.info(f"✨ ยินดีต้อนรับฮีโร่ {current_user}! ระบบพร้อมทำงาน ปล่อยใยพิมพ์ข้อความมาได้เลยครับ")

# 4. แสดงข้อความเก่าๆ
for msg in current_messages:
    avatar_icon = "🦸‍♂️" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        if "images" in msg:
            st.image(msg["images"], width=250)
        elif "image" in msg:
            st.image(msg["image"], width=250)
            
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"] is not None:
            st.audio(msg["audio"], format="audio/mp3")

# 5. ช่องสำหรับพิมพ์ข้อความ
if user_input := st.chat_input("ป้อนข้อความที่นี่..."):
    
    if uploaded_files:
        imgs = [Image.open(f) for f in uploaded_files]
        current_messages.append({"role": "user", "content": user_input, "images": imgs})
        content_to_send = imgs + [user_input]
    else:
        current_messages.append({"role": "user", "content": user_input})
        content_to_send = [user_input]

    save_chat_to_sheet(current_user, current_topic, "user", user_input)

    with st.chat_message("user", avatar="🦸‍♂️"):
        if uploaded_files:
            st.image(imgs, width=250)
        st.markdown(user_input)
    
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        sound_placeholder = st.empty()
        
        with st.spinner("🕷️ สไปเดอร์เซนส์กำลังทำงาน..."):
            try: 
                response = current_instance.send_message(content_to_send)
                ai_text = response.text
                response_placeholder.markdown(ai_text)
                
                save_chat_to_sheet(current_user, current_topic, "assistant", ai_text)
                
                clean_text_for_speech = re.sub(r'[*#`]', '', ai_text)
                sound_bytes = None
                try:
                    sound_file = io.BytesIO()
                    tts = gTTS(text=clean_text_for_speech, lang='th')
                    tts.write_to_fp(sound_file)
                    sound_bytes = sound_file.getvalue()
                    sound_placeholder.audio(sound_bytes, format="audio/mp3")
                except Exception:
                    pass
                    
                current_messages.append({
                    "role": "assistant", 
                    "content": ai_text,
                    "audio": sound_bytes
                })
                
            except Exception as e:
                st.error(f"ระบบขัดข้อง: {e}")

    if uploaded_files:
        st.session_state.uploader_key += 1
        st.rerun()
