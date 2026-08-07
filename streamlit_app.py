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

# ---------- Model selection and API keys ----------
def get_api_keys():
    """Read API keys from Streamlit secrets or environment variables."""
    return {
        "gemini": st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY"),
        "openai": st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"),
        "deepseek": st.secrets.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY"),
    }

API_KEYS = get_api_keys()

# ---------- Sidebar: Model selection & status ----------
with st.sidebar:
    st.header("⚙️ frest Settings")

    model_choice = st.selectbox(
        "Choose AI model",
        ["Gemini (Google)", "ChatGPT (OpenAI)", "DeepSeek"],
        index=0,
        help="Select which AI engine to power frest."
    )

    # Show API key status
    st.subheader("🔑 API Keys")
    for name, key in API_KEYS.items():
        status = "✅" if key else "❌"
        st.write(f"{status} {name.capitalize()}")

    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Your API keys are stored securely in secrets or environment variables.")

# ---------- Model initialization ----------
def get_gemini_response(messages: List[Dict[str, str]]) -> str:
    import google.generativeai as genai

    genai.configure(api_key=API_KEYS["gemini"])
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=SYSTEM_PROMPT,
    )
    # Convert messages to Gemini format
    history = []
    for msg in messages[:-1]:  # all but the last user message
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"])
    return response.text

def get_openai_response(messages: List[Dict[str, str]]) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=API_KEYS["openai"])
    # Build messages list with system prompt
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4" if you have access
        messages=full_messages,
        temperature=0.7,
    )
    return response.choices[0].message.content

def get_deepseek_response(messages: List[Dict[str, str]]) -> str:
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

    # Get response based on selected model
    with st.chat_message("assistant"):
        with st.spinner(f"Consulting {model_choice}..."):
            try:
                # Map choice to API key and function
                if model_choice == "Gemini (Google)":
                    if not API_KEYS["gemini"]:
                        raise ValueError("Gemini API key not set.")
                    reply = get_gemini_response(st.session_state.messages)
                elif model_choice == "ChatGPT (OpenAI)":
                    if not API_KEYS["openai"]:
                        raise ValueError("OpenAI API key not set.")
                    reply = get_openai_response(st.session_state.messages)
                elif model_choice == "DeepSeek":
                    if not API_KEYS["deepseek"]:
                        raise ValueError("DeepSeek API key not set.")
                    reply = get_deepseek_response(st.session_state.messages)
                else:
                    reply = "Unknown model selected."

                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.info("Make sure your API key is correct and you have credits.")

# ---------- Footer ----------
st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tips**\n"
    "- Switch models anytime – frest adapts.\n"
    "- The system prompt ensures expert responses.\n"
    "- Your chat history stays in the session."
)