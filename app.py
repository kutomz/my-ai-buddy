from gtts import gTTS
import io
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. ตั้งค่าหน้าตาแอปหลัก
st.set_page_config(page_title="My AI Buddy", page_icon="🤖", layout="centered")
st.title("✨ My AI Robot Boys")
st.caption("ผู้ช่วยส่วนตัวสุดฉลาดของคุณ (เวอร์ชันแก้ทรงลุง 🛡️)")

# 2. เริ่มต้นการเชื่อมต่อ
if "ai_client" not in st.session_state:
    # 🔐 ดึง API Key จากตู้เซฟลับของ Streamlit
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    
    st.session_state.ai_client = genai.Client(api_key=GOOGLE_API_KEY)
    # 🛠️ ปิดระบบค้นหาเน็ตชั่วคราว เพื่อป้องกัน Error ตอนที่น้องอัปโหลดรูปให้ AI ดู
    st.session_state.chat_session = st.session_state.ai_client.chats.create(
        model="gemini-1.5-flash"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. ตกแต่งเมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=100)
    st.header("📸 อัปโหลดรูปภาพ")
    uploaded_file = st.file_uploader("ส่งรูปให้ AI วิเคราะห์", type=["jpg", "jpeg", "png"])
    
    st.divider()
    
    st.header("⚙️ จัดการระบบ")
    if st.button("🗑️ เริ่มแชทใหม่", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = st.session_state.ai_client.chats.create(
            model="gemini-1.5-flash"
        )
        st.rerun()
        
    if len(st.session_state.messages) > 0:
        chat_text = "ประวัติการสนทนา\n" + "="*20 + "\n\n"
        for msg in st.session_state.messages:
            role = "คุณ" if msg["role"] == "user" else "AI Buddy"
            chat_text += f"{role}: {msg['content']}\n\n"
            
        st.download_button(
            label="💾 ดาวน์โหลดประวัติแชท",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- กล่องข้อความต้อนรับ ---
if len(st.session_state.messages) == 0:
    st.info("👋 สวัสดีครับ! ผมคือ AI RobotBoys ของสกาย ลองพิมพ์ทักทาย, ถามข้อมูล หรือส่งรูปมาให้ผมดูที่แถบด้านซ้ายได้เลยครับ")

# 4. แสดงข้อความเก่าๆ 
for msg in st.session_state.messages:
    avatar_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        if "image" in msg:
            st.image(msg["image"], width=300)
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"] is not None:
            st.audio(msg["audio"], format="audio/mp3")

# 5. ช่องสำหรับพิมพ์ข้อความ
if user_input := st.chat_input("พิมพ์ข้อความที่นี่..."):
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.session_state.messages.append({"role": "user", "content": user_input, "image": img})
        content_to_send = [img, user_input]
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        content_to_send = [user_input]

    with st.chat_message("user", avatar="🧑‍💻"):
        if uploaded_file is not None:
            st.image(img, width=300)
        st.markdown(user_input)
    
    # ฝั่ง AI
    with st.chat_message("assistant", avatar="🤖"):
        response_placeholder = st.empty()
        sound_placeholder = st.empty()
        
        with st.spinner("กำลังประมวลผล... ✨"):
            try: 
                # 🛡️ ลองส่งข้อความไปหา Google (ถ้าแครช มันจะเด้งไปทำคำสั่ง except ทันที)
                response = st.session_state.chat_session.send_message(content_to_send)
                ai_text = response.text
                response_placeholder.markdown(ai_text)
                
                sound_bytes = None
                try:
                    sound_file = io.BytesIO()
                    tts = gTTS(text=ai_text, lang='th')
                    tts.write_to_fp(sound_file)
                    sound_bytes = sound_file.getvalue()
                    sound_placeholder.audio(sound_bytes, format="audio/mp3")
                except Exception:
                    pass
                    
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": ai_text,
                    "audio": sound_bytes
                })
                
            except Exception as e:
                # 🚨 ถ้า Google ขัดข้อง จะขึ้นข้อความนี้แทนจอแดง
                st.error(f"ระบบขัดข้องชั่วคราวจากเซิร์ฟเวอร์: {e}")
                st.info("💡 คำแนะนำ: ลองกดปุ่ม '🗑️ เริ่มแชทใหม่' ที่เมนูด้านซ้าย แล้วพิมพ์คุยใหม่อีกครั้งดูนะครับ")
