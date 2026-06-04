from gtts import gTTS
import io
import re
import requests
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. ตั้งค่าหน้าตาแอปหลัก
st.set_page_config(page_title="My AI Robot Boys", page_icon="✨", layout="wide")

# --- 🎨 เวทมนตร์ CSS ตกแต่งหน้าตา ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stChatMessage { background-color: transparent !important; border: none !important; padding: 1.5rem 0 !important; }
    .stMarkdown p { font-size: 16px; line-height: 1.6; }
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

# --- 🔐 ระบบล็อกอินอย่างง่าย ---
if "logged_in" not in st.session_state:
    st.markdown("<h2 style='text-align: center;'>🤖 เข้าสู่ระบบ My AI Robot Boys</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("ชื่อผู้ใช้งาน (Username)")
        password = st.text_input("รหัสผ่าน (Password)", type="password")
        if st.button("เข้าสู่ระบบ 🚀", use_container_width=True):
            # ตั้งค่าบัญชีใช้งานง่ายๆ ในครอบครัว
            if username.lower() == "sky" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.user = "sky"
                st.rerun()
            elif username.lower() == "daddy" and password == "5678":
                st.session_state.logged_in = True
                st.session_state.user = "daddy"
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    st.stop()

# --- 🏠 เข้าสู่หน้าแอปหลักหลังจากล็อกอินผ่านแล้ว ---
current_user = st.session_state.user

# ดึงข้อมูลจากฐานข้อมูล Google Sheet มาตั้งต้นระบบจำห้องแชท
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
    st.session_state.chat_instances = {}
    
    # ดึงประวัติแชทเก่าจากฐานข้อมูลมาโหลดใส่แอป
    db_data = load_chat_from_sheet()
    
    # กรองเอาเฉพาะข้อมูลของคนที่ล็อกอินอยู่ปัจจุบัน
    for row in db_data:
        if len(row) >= 4:
            db_user, db_room, db_role, db_msg = row[0], row[1], row[2], row[3]
            if db_user == current_user:
                if db_room not in st.session_state.chat_sessions:
                    st.session_state.chat_sessions[db_room] = []
                st.session_state.chat_sessions[db_room].append({"role": db_role, "content": db_msg})

    # ถ้ายังไม่มีห้องแชทเลย ให้สร้างห้องแรกขึ้นมาเป็นมาตรฐาน
    if not st.session_state.chat_sessions:
        st.session_state.chat_sessions = {"แชทห้องที่ 1": []}

    # สร้างสมอง AI ผูกไว้กับแต่ละห้องแชทที่มีอยู่
    for room in st.session_state.chat_sessions.keys():
        st.session_state.chat_instances[room] = st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction=f"คุณคือ 'AI RobotBoys' ผู้ช่วยส่วนตัวสุดฉลาดของคุญ {current_user} ให้จำไว้เสมอว่าครอบครัวนี้อาศัยอยู่ที่ย่านรามอินทรา กม.8 กรุงเทพมหานคร เวลาแนะนำข้อมูลให้เน้นพิกัดนี้เป็นหลัก"
            )
        )

if "current_topic" not in st.session_state:
    st.session_state.current_topic = list(st.session_state.chat_sessions.keys())[0]
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# 3. ตกแต่งเมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.title(f"👤 คุณ: {current_user.upper()}")
    if st.button("🚪 ออกจากระบบ", use_container_width=True):
        del st.session_state.logged_in
        del st.session_state.chat_sessions
        st.rerun()
        
    st.markdown("---")
    st.header("🗂️ ประวัติการสนทนา")
    if st.button("➕ เริ่มแชทใหม่", use_container_width=True):
        new_room_name = f"แชทห้องที่ {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_room_name] = []
        st.session_state.chat_instances[new_room_name] = st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction=f"คุณคือ 'AI RobotBoys' ผู้ช่วยส่วนตัวสุดฉลาดของคุญ {current_user} ให้จำไว้เสมอว่าครอบครัวนี้อาศัยอยู่ที่ย่านรามอินทรา กม.8 กรุงเทพมหานคร"
            )
        )
        st.session_state.current_topic = new_room_name
        st.rerun()

    for topic in list(st.session_state.chat_sessions.keys()):
        btn_label = f"💬 {topic}" if topic == st.session_state.current_topic else f"  {topic}"
        if st.button(btn_label, use_container_width=True):
            st.session_state.current_topic = topic
            st.rerun()
            
    st.markdown("---")
    st.header("📸 แนบรูปภาพให้ AI")
    uploaded_files = st.file_uploader(
        "อัปโหลดรูปภาพ", type=["jpg", "jpeg", "png"], 
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed", accept_multiple_files=True 
    )

current_topic = st.session_state.current_topic
current_messages = st.session_state.chat_sessions[current_topic]
current_instance = st.session_state.chat_instances[current_topic]

st.title("✨ My AI Robot Boys")
st.caption(f"กำลังคุยใน: {current_topic} (ประวัติจะถูกบันทึกลง Google Sheet อัตโนมัติ 📊)")

if len(current_messages) == 0:
    st.info(f"✨ ยินดีต้อนรับคุณ {current_user}! ประวัติห้องนี้ว่างอยู่ เริ่มพิมพ์คุยได้เลยครับ")

# 4. แสดงข้อความเก่าๆ
for msg in current_messages:
    avatar_icon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"] is not None:
            st.audio(msg["audio"], format="audio/mp3")

# 5. ช่องสำหรับพิมพ์ข้อความ
if user_input := st.chat_input("ป้อนข้อความที่นี่..."):
    
    if uploaded_files:
        imgs = [Image.open(f) for f in uploaded_files]
        current_messages.append({"role": "user", "content": user_input})
        content_to_send = imgs + [user_input]
    else:
        current_messages.append({"role": "user", "content": user_input})
        content_to_send = [user_input]

    # บันทึกข้อความผู้ใช้ลง Google Sheet หลังบ้านทันที
    save_chat_to_sheet(current_user, current_topic, "user", user_input)

    with st.chat_message("user", avatar="👤"):
        if uploaded_files:
            st.image(imgs, width=250)
        st.markdown(user_input)
    
    with st.chat_message("assistant", avatar="✨"):
        response_placeholder = st.empty()
        sound_placeholder = st.empty()
        
        with st.spinner("กำลังประมวลผล..."):
            try: 
                response = current_instance.send_message(content_to_send)
                ai_text = response.text
                response_placeholder.markdown(ai_text)
                
                # บันทึกคำตอบของ AI ลง Google Sheet หลังบ้านทันที
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
