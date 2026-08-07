"""
streamlit_app.py – frest: AEC & MEP Expert for East Africa
Powered by Gemini, ChatGPT (OpenAI), and DeepSeek.
"""

import streamlit as st
import os
import sys
from typing import List, Dict

# ---------- Page config ----------
st.set_page_config(page_title="frest – AEC Expert", page_icon="🏗️", layout="wide")

# ========== DEBUG: verify secrets file is being read ==========
# This block will show helpful info only if secrets are missing.
# Remove after you see it's working.

if not st.secrets:
    st.warning("⚠️ No secrets found. Make sure your .streamlit/secrets.toml is in the right place.")
    cwd = os.getcwd()
    st.write(f"📂 Current working directory: `{cwd}`")
    streamlit_folder = os.path.join(cwd, ".streamlit")
    if os.path.exists(streamlit_folder):
        st.write("✅ `.streamlit/` folder exists.")
        secrets_file = os.path.join(streamlit_folder, "secrets.toml")
        if os.path.exists(secrets_file):
            st.write("✅ `secrets.toml` file exists.")
            with open(secrets_file, "r") as f:
                content = f.read()
                st.write("📄 File content (masked):")
                # Show only first line to avoid exposing full keys
                lines = content.splitlines()
                for line in lines:
                    if "=" in line:
                        key = line.split("=")[0].strip()
                        st.write(f"   - {key} = ********")
        else:
            st.error("❌ `secrets.toml` file NOT found in `.streamlit/`.")
    else:
        st.error("❌ `.streamlit/` folder NOT found in the current directory.")
    st.stop()  # Stop execution so user can fix the path

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

# ---------- API keys (read directly from st.secrets) ----------
# We use .get() with empty string fallback, but the debug above ensures st.secrets is non-empty.
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "")
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY", "")
DEEPSEEK_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

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
    st.write("✅" if GEMINI_KEY else "❌", " Gemini")
    st.write("✅" if OPENAI_KEY else "❌", " OpenAI")
    st.write("✅" if DEEPSEEK_KEY else "❌", " DeepSeek")

    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Keys are read from .streamlit/secrets.toml or environment variables.")

# ---------- Model functions ----------
def call_gemini(messages: List[Dict[str, str]]) -> str:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=SYSTEM_PROMPT,
    )
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"])
    return response.text

def call_openai(messages: List[Dict[str, str]]) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=full_messages,
        temperature=0.7,
    )
    return response.choices[0].message.content

def call_deepseek(messages: List[Dict[str, str]]) -> str:
    from openai import OpenAI
    client = OpenAI(
        api_key=DEEPSEEK_KEY,
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

    # Map model choice to key and function
    model_map = {
        "Gemini (Google)": (GEMINI_KEY, call_gemini, "Gemini"),
        "ChatGPT (OpenAI)": (OPENAI_KEY, call_openai, "OpenAI"),
        "DeepSeek": (DEEPSEEK_KEY, call_deepseek, "DeepSeek"),
    }
    api_key, call_func, model_name = model_map[model_choice]

    if not api_key:
        with st.chat_message("assistant"):
            st.error(f"❌ {model_name} API key is not set. Please add it to your secrets.")
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