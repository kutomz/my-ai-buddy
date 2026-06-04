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
