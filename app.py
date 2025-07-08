import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="PictoQuery", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 330px;
        }
        [data-testid="collapsedControl"] { display: none; }

        .block-container { padding: 1rem; }

        .chat-box {
            display: flex; flex-direction: column; gap: 10px;
            max-height: 72vh; overflow-y: auto;
            padding: 10px; background-color: #101010; border-radius: 8px;
        }
        .msg {
            padding: 10px 14px;
            border-radius: 12px;
            display: inline-block;
            font-size: 15px;
            max-width: 100%;
            word-break: break-word;
        }
        .user { align-self: flex-end; background: #2C2C2C; color: white; }
        .bot  { align-self: flex-start; background: #333; color: white; }

        .chat-pair {
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

genai.configure(api_key=st.secrets.get("Gemini_API_Key"))  

if "chat" not in st.session_state:
    st.session_state.chat = []
if "img_bytes" not in st.session_state:
    st.session_state.img_bytes = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>PictoQuery</h1>", unsafe_allow_html=True)

sidebar, main = st.columns([1, 3], gap="large")

with sidebar:
    st.header("📸 Upload Image")
    uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if uploaded:
        st.session_state.img_bytes = uploaded.read()
        st.image(st.session_state.img_bytes, caption=uploaded.name, use_container_width=True)

with main:
    st.header("💬 Ask About Your Image")

    with st.form("chat_form", clear_on_submit=True):
        prompt = st.text_input("Your question...", key="user_input")
        submitted = st.form_submit_button("Send")
        if submitted and prompt and st.session_state.img_bytes:
            st.session_state.chat.append(("user", prompt))
            try:
                image = Image.open(io.BytesIO(st.session_state.img_bytes))
                model = genai.GenerativeModel("gemini-1.5-flash")
                with st.spinner("Thinking..."):
                    response = model.generate_content([prompt, image])
                answer = response.text.strip()
            except Exception as e:
                answer = f"⚠️ Error: {e}"
            st.session_state.chat.append(("bot", answer))
            st.session_state.submitted = True
            st.rerun()

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    chat = st.session_state.chat
    for i in range(0, len(chat), 2):
        st.markdown('<div class="chat-pair">', unsafe_allow_html=True)

        for j in range(2):  
            if i + j < len(chat):
                role, msg = chat[i + j]
                css = "user" if role == "user" else "bot"
                st.markdown(f'<div class="msg {css}">{msg}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)