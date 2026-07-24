import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/api/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro")

    # Find the last user message and build history
    last_user_idx = -1
    for i, msg in enumerate(req.messages):
        if msg["role"] == "user":
            last_user_idx = i

    if last_user_idx == -1:
        raise HTTPException(status_code=400, detail="No user message found")

    last_prompt = req.messages[last_user_idx]["content"]
    history = []
    for i, msg in enumerate(req.messages):
        if i >= last_user_idx:
            break
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    try:
        chat = model.start_chat(history=history)
        response = chat.send_message(last_prompt)
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok"}