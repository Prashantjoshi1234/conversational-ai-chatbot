import streamlit as st
import requests
import uuid
import sys
import os

# ----------------------------
# Path Fix (IMPORTANT)
# ----------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

# ----------------------------
# Configuration
# ----------------------------
API_URL = "http://127.0.0.1:8000/api/chat"
NEW_CHAT_API = "http://127.0.0.1:8000/api/session/clear"

st.set_page_config(
    page_title="Conversational AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ----------------------------
# Session Init
# ----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------
# Sidebar Controls
# ----------------------------
with st.sidebar:
    if st.button("🆕 New Chat"):
        # Clear backend memory
        try:
            response = requests.post(
                NEW_CHAT_API,
                json={"session_id": st.session_state.session_id},
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            st.warning(f"Backend session clear failed: {e}")

        # Clear frontend chat history
        st.session_state.chat_history = []

        # New session_id
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# ----------------------------
# Main UI
# ----------------------------
st.image("frontend/assets/klearcom1.png")
st.title("Klearcom Chatbot Assistant")
st.caption("How can we help you understand our company better?")

# Show chat history
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

        if chat.get("sources"):
            with st.expander("Sources"):
                for src in chat["sources"]:
                    st.write(src)

# ----------------------------
# Chat Input
# ----------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message instantly
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    payload = {
        "session_id": st.session_state.session_id,
        "message": user_input
    }

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            try:
                response = requests.post(API_URL, json=payload, timeout=300)
                response.raise_for_status()

                data = response.json()
                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])

            except Exception as e:
                answer = f"❌ Backend error: {e}"
                sources = []

            st.write(answer)

            DEBUG = True

            if DEBUG and sources:
                with st.expander("Sources"):
                    for src in sources:
                        st.write(src)

    # Save assistant reply to UI history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
