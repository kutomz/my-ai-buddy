from gtts import gTTS
import io
import re
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. ตั้งค่าหน้าตาแอปหลัก
st.set_page_config(page_title="My AI Robot Boys", page_icon="✨", layout="wide")

# --- 🎨 เริ่มต้นเวทมนตร์ CSS ตกแต่งหน้าตา (สไตล์คลีนๆ แบบ Gemini) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1.5rem 0 !important;
    }
    
    .stMarkdown p {
        font-size: 16px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)
# --- จบเวทมนตร์ CSS ---

st.title("✨ My AI Robot Boys")
st.caption("ผู้ช่วยส่วนตัวสุดฉลาดของคุณ (เวอร์ชัน 5.0: ส่งรูปได้ทีละหลายๆ รูปแล้ว 📸)")

# 2. เริ่มต้นการเชื่อมต่อ
if "ai_client" not in st.session_state:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    st.session_state.ai_client = genai.Client(api_key=GOOGLE_API_KEY)

# --- ระบบจัดการห้องแชท (Topic Sessions) ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"แชทห้องที่ 1": []}
if "chat_instances" not in st.session_state:
    st.session_state.chat_instances = {
        "แชทห้องที่ 1": st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction="คุณคือ 'AI RobotBoys' ผู้ช่วยส่วนตัวสุดฉลาดของน้องสกาย ให้จำไว้เสมอว่าครอบครัวของสกายอาศัยอยู่ที่ย่านรามอินทรา กม.8 กรุงเทพมหานคร เวลาแนะนำสถานที่เที่ยว ร้านอาหาร หรือข้อมูลการเดินทาง ให้เน้นอ้างอิงจากแถวรามอินทรา กม.8 เป็นหลัก"
            )
        )
    }
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "แชทห้องที่ 1"
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# 3. ตกแต่งเมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.title("เมนูหลัก")
    st.markdown("---")
    
    st.header("🗂️ ประวัติการสนทนา")
    if st.button("➕ เริ่มแชทใหม่", use_container_width=True):
        new_room_name = f"แชทห้องที่ {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_room_name] = []
        st.session_state.chat_instances[new_room_name] = st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction="คุณคือ 'AI RobotBoys' ผู้ช่วยส่วนตัวสุดฉลาดของน้องสกาย ให้จำไว้เสมอว่าครอบครัวของสกายอาศัยอยู่ที่ย่านรามอินทรา กม.8 กรุงเทพมหานคร เวลาแนะนำสถานที่เที่ยว ร้านอาหาร หรือข้อมูลการเดินทาง ให้เน้นอ้างอิงจากแถวรามอินทรา กม.8 เป็นหลัก"
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
    
    # 🛠️ จุดที่แก้: เปิดโหมดรับหลายไฟล์ (accept_multiple_files=True)
    uploaded_files = st.file_uploader(
        "อัปโหลดได้หลายรูปพร้อมกัน", 
        type=["jpg", "jpeg", "png"], 
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed",
        accept_multiple_files=True 
    )

current_topic = st.session_state.current_topic
current_messages = st.session_state.chat_sessions[current_topic]
current_instance = st.session_state.chat_instances[current_topic]

if len(current_messages) == 0:
    st.info(f"✨ ยินดีต้อนรับสู่ **{current_topic}**! ส่งรูปมาหลายๆ รูปพร้อมกันได้เลยนะครับ")

# 4. แสดงข้อความเก่าๆ 
for msg in current_messages:
    avatar_icon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        # 🛠️ จุดที่แก้: ให้รองรับการแสดงรูปภาพแบบหลายรูป (images) และแบบเก่ารูปเดียว (image)
        if "images" in msg:
            st.image(msg["images"], width=250)
        elif "image" in msg:
            st.image(msg["image"], width=250)
            
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"] is not None:
            st.audio(msg["audio"], format="audio/mp3")

# 5. ช่องสำหรับพิมพ์ข้อความ
if user_input := st.chat_input("ป้อนข้อความที่นี่..."):
    
    # 🛠️ จุดที่แก้: เตรียมข้อมูลรูปภาพทั้งหมดเพื่อส่งให้ AI
    if uploaded_files:
        imgs = [Image.open(f) for f in uploaded_files]
        current_messages.append({"role": "user", "content": user_input, "images": imgs})
        content_to_send = imgs + [user_input]
    else:
        current_messages.append({"role": "user", "content": user_input})
        content_to_send = [user_input]

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
                st.info("💡 ลองรีเฟรชหน้าเว็บ หรือสร้างห้องแชทใหม่ดูนะครับ")

    # 🛠️ จุดที่แก้: ถ้ามีการอัปโหลดไฟล์ ให้เคลียร์กล่องอัปโหลด
    if uploaded_files:
        st.session_state.uploader_key += 1
        st.rerun()
