"""
streamlit_app.py – frest: AEC & MEP Expert for East Africa
"""

import streamlit as st
import os
from typing import List, Dict

# ---------- Load environment variables from .env (if present) ----------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed – that's fine

# ---------- Page config ----------
st.set_page_config(page_title="frest – AEC Expert", page_icon="🏗️", layout="wide")

# ---------- Helper to get keys ----------
def get_key(name: str) -> str:
    """Try st.secrets, then environment, then empty."""
    try:
        val = st.secrets.get(name, "")
        if val:
            return val
    except:
        pass
    return os.getenv(name, "")

GEMINI_KEY = get_key("GEMINI_API_KEY")
OPENAI_KEY = get_key("OPENAI_API_KEY")
DEEPSEEK_KEY = get_key("DEEPSEEK_API_KEY")

# ---------- If no keys, show detailed guidance ----------
if not any([GEMINI_KEY, OPENAI_KEY, DEEPSEEK_KEY]):
    st.error("🔑 No API keys found!")
    st.markdown("""
    **Please set your keys using one of these methods:**
    
    1. **`.streamlit/secrets.toml`** (local or cloud):
       - Folder must be named `.streamlit` (with a dot)
       - File must be named `secrets.toml`
       - Content example:
         ```toml
         GEMINI_API_KEY = "AIzaSy..."
         DEEPSEEK_API_KEY = "sk-..."
         ```
    
    2. **Environment variables** (local):
       ```bash
       export GEMINI_API_KEY="AIzaSy..."
       export DEEPSEEK_API_KEY="sk-..."
       streamlit run streamlit_app.py
       ```
    
    3. **`.env` file** (local) – install `python-dotenv`:
       ```
       GEMINI_API_KEY=AIzaSy...
       DEEPSEEK_API_KEY=sk-...
       ```
    """)
    # Show current directory and file check
    cwd = os.getcwd()
    st.write(f"📂 Current directory: `{cwd}`")
    streamlit_dir = os.path.join(cwd, ".streamlit")
    if os.path.exists(streamlit_dir):
        st.write("✅ `.streamlit/` folder exists.")
        secrets_file = os.path.join(streamlit_dir, "secrets.toml")
        if os.path.exists(secrets_file):
            st.write("✅ `secrets.toml` exists.")
        else:
            st.write("❌ `secrets.toml` missing inside `.streamlit/`.")
    else:
        st.write("❌ `.streamlit/` folder not found.")
    st.stop()

# ---------- System prompt ----------
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

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ frest Settings")
    model_choice = st.selectbox(
        "Choose AI model",
        ["Gemini (Google)", "ChatGPT (OpenAI)", "DeepSeek"],
        index=0,
    )
    st.subheader("🔑 API Key Status")
    st.write("✅" if GEMINI_KEY else "❌", " Gemini")
    st.write("✅" if OPENAI_KEY else "❌", " OpenAI")
    st.write("✅" if DEEPSEEK_KEY else "❌", " DeepSeek")

    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

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

# ---------- Chat ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🏗️ Hello! I'm frest, your AEC expert for East Africa. How can I assist you today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about construction, MEP, materials, or East African projects..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    model_map = {
        "Gemini (Google)": (GEMINI_KEY, call_gemini, "Gemini"),
        "ChatGPT (OpenAI)": (OPENAI_KEY, call_openai, "OpenAI"),
        "DeepSeek": (DEEPSEEK_KEY, call_deepseek, "DeepSeek"),
    }
    api_key, call_func, model_name = model_map[model_choice]

    if not api_key:
        with st.chat_message("assistant"):
            st.error(f"❌ {model_name} API key is not set.")
        st.stop()

    with st.chat_message("assistant"):
        with st.spinner(f"Consulting {model_choice}..."):
            try:
                reply = call_func(st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                st.info("Check your API key and internet connection.")