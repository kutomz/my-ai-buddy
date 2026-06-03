from gtts import gTTS
import io
import re
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. ตั้งค่าหน้าตาแอปหลัก
st.set_page_config(page_title="My AI Robot Boys", page_icon="🤖", layout="wide")
st.title("✨ My AI Robot Boys")
st.caption("ผู้ช่วยส่วนตัวสุดฉลาดของคุณ (เวอร์ชัน 3.0: มีหลายห้องแชท + ต่อเน็ตแล้ว 🌐)")

# 2. เริ่มต้นการเชื่อมต่อ
if "ai_client" not in st.session_state:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    st.session_state.ai_client = genai.Client(api_key=GOOGLE_API_KEY)

# --- ระบบจัดการห้องแชท (Topic Sessions) ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"แชทห้องที่ 1": []} # เก็บข้อความของแต่ละห้อง
if "chat_instances" not in st.session_state:
    # 🛠️ ใช้สมองรุ่น 2.5 ที่ฉลาดที่สุดและต่อเน็ตค้นหาข้อมูลได้
    st.session_state.chat_instances = {
        "แชทห้องที่ 1": st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(tools=[{"google_search": {}}])
        )
    }
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "แชทห้องที่ 1" # ห้องที่กำลังเปิดอยู่
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0 # ตัวแปรสำหรับเคลียร์รูปภาพ

# 3. ตกแต่งเมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=100)
    
    st.header("📸 อัปโหลดรูปภาพ")
    # ใส่ key เพื่อให้สามารถสั่งรีเซ็ตช่องอัปโหลดได้
    uploaded_file = st.file_uploader(
        "ส่งรูปให้ AI วิเคราะห์", 
        type=["jpg", "jpeg", "png"], 
        key=f"uploader_{st.session_state.uploader_key}"
    )
    
    st.divider()
    
    st.header("🗂️ ห้องแชทของคุณ")
    if st.button("➕ สร้างห้องแชทใหม่", use_container_width=True):
        new_room_name = f"แชทห้องที่ {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_room_name] = []
        # 🛠️ ใช้สมองรุ่น 2.5 สำหรับห้องแชทใหม่
        st.session_state.chat_instances[new_room_name] = st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(tools=[{"google_search": {}}])
        )
        st.session_state.current_topic = new_room_name
        st.rerun()

    st.markdown("---")
    
    # แสดงปุ่มห้องแชททั้งหมด
    for topic in list(st.session_state.chat_sessions.keys()):
        # ไฮไลท์สีให้รู้ว่าตอนนี้อยู่ห้องไหน
        btn_label = f"🟢 {topic}" if topic == st.session_state.current_topic else f"⚪ {topic}"
        if st.button(btn_label, use_container_width=True):
            st.session_state.current_topic = topic
            st.rerun()

# ดึงข้อมูลของห้องแชทปัจจุบันมาใช้งาน
current_topic = st.session_state.current_topic
current_messages = st.session_state.chat_sessions[current_topic]
current_instance = st.session_state.chat_instances[current_topic]

# --- กล่องข้อความต้อนรับ ---
if len(current_messages) == 0:
    st.info(f"👋 ยินดีต้อนรับสู่ **{current_topic}**! พิมพ์ทักทาย, ถามข้อมูลค้นหาจากเน็ต หรือส่งรูปมาให้ผมดูได้เลยครับ")

# 4. แสดงข้อความเก่าๆ ในห้องนี้
for msg in current_messages:
    avatar_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        if "image" in msg:
            st.image(msg["image"], width=300)
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"] is not None:
            st.audio(msg["audio"], format="audio/mp3")

# 5. ช่องสำหรับพิมพ์ข้อความ
if user_input := st.chat_input("พิมพ์ข้อความที่นี่..."):
    
    # จัดเตรียมข้อมูลฝั่งผู้ใช้
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        current_messages.append({"role": "user", "content": user_input, "image": img})
        content_to_send = [img, user_input]
    else:
        current_messages.append({"role": "user", "content": user_input})
        content_to_send = [user_input]

    # แสดงข้อความฝั่งผู้ใช้ทันที
    with st.chat_message("user", avatar="🧑‍💻"):
        if uploaded_file is not None:
            st.image(img, width=300)
        st.markdown(user_input)
    
    # ฝั่ง AI ประมวลผล
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        sound_placeholder = st.empty()
        
        with st.spinner("กำลังค้นหาและประมวลผล... ✨"):
            try: 
                response = current_instance.send_message(content_to_send)
                ai_text = response.text
                response_placeholder.markdown(ai_text)
                
                # --- ลบสัญลักษณ์พิเศษก่อนส่งให้ระบบเสียงอ่าน ---
                # ลบเครื่องหมาย * และ # และ ` ออกไป จะได้ไม่อ่านว่า ดอกจัน
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
                st.error(f"ระบบขัดข้องชั่วคราว: {e}")
                st.info("💡 คำแนะนำ: โควต้าอาจจะเต็ม หรืออินเทอร์เน็ตมีปัญหา ลองสร้างห้องแชทใหม่ดูนะครับ")

    # สั่งให้เคลียร์รูปภาพที่เคยอัปโหลดไว้ แล้วรีเฟรชจอ 1 ครั้ง
    if uploaded_file is not None:
        st.session_state.uploader_key += 1
        st.rerun()
