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
    /* ซ่อนเมนูขวาบนและข้อความ Streamlit ด้านล่าง */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ระยะห่างของหน้าจอโดยรวม ให้ดูไม่อึดอัด */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ปรับกล่องข้อความแชทให้ไม่มีพื้นหลัง (โปร่งใส) คล้าย Gemini */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 1.5rem 0 !important;
    }
    
    /* ปรับขนาดตัวอักษรให้พอดี อ่านง่าย */
    .stMarkdown p {
        font-size: 16px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)
# --- จบเวทมนตร์ CSS ---

st.title("✨ My AI Robot Boys")
st.caption("ผู้ช่วยส่วนตัวสุดฉลาดของคุณ (เวอร์ชัน 4.0: ดีไซน์คลีนสไตล์ Gemini 🌌)")

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

    # แสดงปุ่มห้องแชททั้งหมด
    for topic in list(st.session_state.chat_sessions.keys()):
        btn_label = f"💬 {topic}" if topic == st.session_state.current_topic else f"  {topic}"
        if st.button(btn_label, use_container_width=True):
            st.session_state.current_topic = topic
            st.rerun()
            
    st.markdown("---")
    st.header("📸 แนบรูปภาพให้ AI")
    uploaded_file = st.file_uploader(
        "รองรับ JPG, JPEG, PNG", 
        type=["jpg", "jpeg", "png"], 
        key=f"uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed" # ซ่อนตัวหนังสือให้ดูคลีนขึ้น
    )

# ดึงข้อมูลของห้องแชทปัจจุบันมาใช้งาน
current_topic = st.session_state.current_topic
current_messages = st.session_state.chat_sessions[current_topic]
current_instance = st.session_state.chat_instances[current_topic]

# --- กล่องข้อความต้อนรับ ---
if len(current_messages) == 0:
    st.info(f"✨ ยินดีต้อนรับสู่ **{current_topic}**! ผมพร้อมตอบคำถาม ค้นหาข้อมูลจากเน็ต หรือวิเคราะห์รูปภาพแล้วครับ")

# 4. แสดงข้อความเก่าๆ ในห้องนี้
for msg in current_messages:
    # เปลี่ยนอวตารให้คล้าย Gemini
    avatar_icon = "👤" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        if "image" in msg:
            st.image(msg["image"], width=250) # ปรับขนาดรูปให้เล็กลงนิดนึงจะได้ดูสมูท
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"] is not None:
            st.audio(msg["audio"], format="audio/mp3")

# 5. ช่องสำหรับพิมพ์ข้อความ
if user_input := st.chat_input("ป้อนข้อความที่นี่..."):
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        current_messages.append({"role": "user", "content": user_input, "image": img})
        content_to_send = [img, user_input]
    else:
        current_messages.append({"role": "user", "content": user_input})
        content_to_send = [user_input]

    with st.chat_message("user", avatar="👤"):
        if uploaded_file is not None:
            st.image(img, width=250)
        st.markdown(user_input)
    
    # ฝั่ง AI ประมวลผล
    with st.chat_message("assistant", avatar="✨"):
        response_placeholder = st.empty()
        sound_placeholder = st.empty()
        
        with st.spinner("กำลังประมวลผล..."):
            try: 
                response = current_instance.send_message(content_to_send)
                ai_text = response.text
                response_placeholder.markdown(ai_text)
                
                # --- ลบสัญลักษณ์พิเศษก่อนส่งให้ระบบเสียงอ่าน ---
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

    if uploaded_file is not None:
        st.session_state.uploader_key += 1
        st.rerun()
