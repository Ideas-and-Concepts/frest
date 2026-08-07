"""
streamlit_app.py – frest: AEC & MEP Expert for East Africa
Powered by Gemini, ChatGPT (OpenAI), and DeepSeek.
"""

import streamlit as st
import os
from typing import List, Dict

# ---------- Page config ----------
st.set_page_config(page_title="frest – AEC Expert", page_icon="🏗️", layout="wide")

# ---------- System prompt (expert context) ----------
SYSTEM_PROMPT = (
    "You are frest, an expert in Architecture, Engineering, and Construction (AEC), "
    "with deep specialization in Mechanical, Electrical, and Plumbing (MEP) systems. "
    "You have extensive knowledge of the East African construction industry, including "
    "local building codes, materials (e.g., timber, concrete, steel, finishes), "
    "supply chains, climate considerations, and cost estimation. "
    "Provide practical, region-specific advice. Always consider sustainability, "
    "local availability, and cost-effectiveness. Answer in a clear, concise, "
    "and professional manner."
)

# ---------- API key helpers ----------
def get_key(key_name: str) -> str:
    """Return API key from secrets or environment, or empty string."""
    try:
        return st.secrets.get(key_name, os.getenv(key_name, ""))
    except:
        return os.getenv(key_name, "")

API_KEYS = {
    "gemini": get_key("GEMINI_API_KEY"),
    "openai": get_key("OPENAI_API_KEY"),
    "deepseek": get_key("DEEPSEEK_API_KEY"),
}

# ---------- Sidebar: status and settings ----------
with st.sidebar:
    st.header("⚙️ frest Settings")

    model_choice = st.selectbox(
        "Choose AI model",
        ["Gemini (Google)", "ChatGPT (OpenAI)", "DeepSeek"],
        index=0,
        help="Select which AI engine to power frest."
    )

    st.subheader("🔑 API Key Status")
    for name, key in API_KEYS.items():
        status = "✅" if key else "❌"
        st.write(f"{status} {name.capitalize()}")

    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Keys are read from .streamlit/secrets.toml or environment variables.")

# ---------- Model functions ----------
def call_gemini(messages: List[Dict[str, str]]) -> str:
    import google.generativeai as genai
    genai.configure(api_key=API_KEYS["gemini"])
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=SYSTEM_PROMPT,
    )
    # Build history and last user message
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"])
    return response.text

def call_openai(messages: List[Dict[str, str]]) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEYS["openai"])
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4"
        messages=full_messages,
        temperature=0.7,
    )
    return response.choices[0].message.content

def call_deepseek(messages: List[Dict[str, str]]) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key=API_KEYS["deepseek"],
        base_url="https://api.deepseek.com/v1",
    )
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=full_messages,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ---------- Chat logic ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🏗️ Hello! I'm frest, your AEC expert for East Africa. How can I assist you today?"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask about construction, MEP, materials, or East African projects..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Determine which model to call
    model_map = {
        "Gemini (Google)": ("gemini", call_gemini),
        "ChatGPT (OpenAI)": ("openai", call_openai),
        "DeepSeek": ("deepseek", call_deepseek),
    }
    key_name, call_func = model_map[model_choice]

    # Check if API key is available
    if not API_KEYS[key_name]:
        with st.chat_message("assistant"):
            st.error(f"❌ {key_name.capitalize()} API key is not set. Please add it to your secrets.")
        st.stop()

    # Get response
    with st.chat_message("assistant"):
        with st.spinner(f"Consulting {model_choice}..."):
            try:
                reply = call_func(st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                st.info("Check your API key and internet connection.")