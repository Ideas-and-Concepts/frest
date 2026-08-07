import streamlit as st
import os
import sys

st.set_page_config(page_title="Debug Secrets", layout="wide")

st.title("🔍 Secrets Debugger")

# 1. Show st.secrets
st.subheader("1. `st.secrets` content")
st.write("Keys found:", list(st.secrets.keys()))
if st.secrets:
    for k, v in st.secrets.items():
        st.write(f"- {k}: `{v[:8]}...`" if len(v) > 8 else f"- {k}: `{v}`")
else:
    st.error("❌ st.secrets is EMPTY.")

# 2. Show environment variables
st.subheader("2. Environment variables (GEMINI_API_KEY, DEEPSEEK_API_KEY, OPENAI_API_KEY)")
for env in ["GEMINI_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"]:
    val = os.getenv(env)
    if val:
        st.write(f"- {env}: `{val[:8]}...`")
    else:
        st.write(f"- {env}: not set")

# 3. Check file system
st.subheader("3. File system check")
cwd = os.getcwd()
st.write(f"Current working directory: `{cwd}`")
streamlit_dir = os.path.join(cwd, ".streamlit")
if os.path.exists(streamlit_dir):
    st.write("✅ `.streamlit/` folder exists.")
    secrets_file = os.path.join(streamlit_dir, "secrets.toml")
    if os.path.exists(secrets_file):
        st.write("✅ `secrets.toml` exists.")
        with open(secrets_file, "r") as f:
            content = f.read()
            st.text("Content (masked):")
            for line in content.splitlines():
                if "=" in line:
                    key = line.split("=")[0].strip()
                    st.write(f"   {key} = ********")
                else:
                    st.write(f"   {line}")
    else:
        st.error("❌ `secrets.toml` NOT found inside `.streamlit/`.")
else:
    st.error("❌ `.streamlit/` folder NOT found in current directory.")