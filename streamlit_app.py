"""
streamlit_app.py – Gemini Chat Interface
Inspired by the frest Android project (jameswol-ai/frest).
Requires a Gemini API key.
"""

import streamlit as st
import google.generativeai as genai
import os

# ---------- Page config ----------
st.set_page_config(page_title="Gemini Chat (frest style)", page_icon="🤖")
st.title("🤖 Gemini Chat")
st.caption("A Streamlit version of the frest Android app concept")

# ---------- API key handling ----------
# Get the key from Streamlit secrets or environment variable
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 Please set your Gemini API key in `.streamlit/secrets.toml` "
             "or as the environment variable `GEMINI_API_KEY`.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")  # or "gemini-pro"

# ---------- Session state for chat history ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! How can I help you today?"}
    ]

# ---------- Display chat history ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Input and response ----------
if prompt := st.chat_input("Your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build context from history (Gemini expects a list of parts)
                history = [
                    {"role": msg["role"], "parts": [msg["content"]]}
                    for msg in st.session_state.messages[:-1]  # exclude current prompt
                ]
                # Start a new chat with history
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                reply = response.text
                st.markdown(reply)
                # Save assistant reply
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")
