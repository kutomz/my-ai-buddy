import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. ตั้งค่าหน้าตาแอปหลัก
st.set_page_config(page_title="My AI Buddy", page_icon="🤖", layout="centered")
st.title("✨ My AI Buddy")
st.caption("ผู้ช่วยส่วนตัวสุดฉลาดของคุณ (เวอร์ชัน UI อัปเกรด 🚀)")

# 2. เริ่มต้นการเชื่อมต่อ
if "ai_client" not in st.session_state:
    # 🚨 ใส่ API KEY ของคุณตรงนี้ 🚨
    GOOGLE_API_KEY = "AQ.Ab8RN6KdFmLBDFcL387--oshiR4vY2zNHPiQLxHRzanmA5T7Gw"
    
    st.session_state.ai_client = genai.Client(api_key=GOOGLE_API_KEY)
    st.session_state.chat_session = st.session_state.ai_client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(tools=[{"google_search": {}}])
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. ตกแต่งเมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=100) # ใส่รูปโลโก้เท่ๆ
    st.header("📸 อัปโหลดรูปภาพ")
    uploaded_file = st.file_uploader("ส่งรูปให้ AI วิเคราะห์", type=["jpg", "jpeg", "png"])
    
    st.divider()
    
    st.header("⚙️ จัดการระบบ")
    if st.button("🗑️ เริ่มแชทใหม่", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = st.session_state.ai_client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(tools=[{"google_search": {}}])
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

# --- กล่องข้อความต้อนรับ (แสดงเฉพาะตอนยังไม่มีแชท) ---
if len(st.session_state.messages) == 0:
    st.info("👋 สวัสดีครับ! ผมคือ AI Buddy ของคุณ ลองพิมพ์ทักทาย, ถามข้อมูล หรือส่งรูปมาให้ผมดูที่แถบด้านซ้ายได้เลยครับ")

# 4. แสดงข้อความเก่าๆ บนหน้าจอ (พร้อม Avatar)
for msg in st.session_state.messages:
    avatar_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        if "image" in msg:
            st.image(msg["image"], width=300)
        st.markdown(msg["content"])

# 5. ช่องสำหรับพิมพ์ข้อความ
if user_input := st.chat_input("พิมพ์ข้อความที่นี่..."):
    
    # ฝั่งผู้ใช้
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
        with st.spinner("กำลังประมวลผล... ✨"):
            response = st.session_state.chat_session.send_message(content_to_send)
            response_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})