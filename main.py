# main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
from chatbot import chat_with_gemini, JEONSE_CHECKLIST  # import

load_dotenv()
AI_SECRET = os.getenv("AI_SECRET", "")

app = FastAPI(title="B - AI Service")

@app.get("/health")           
async def health():
    return {"ok": True}

def check_key(req: Request):
    if AI_SECRET and req.headers.get("x-ai-key") != AI_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/v1/chat")
async def chat(req: Request, body: dict):
    check_key(req)
    messages = body.get("messages", [])
    return JSONResponse({"reply": reply_text})

@app.get("/v1/chat/stream")
async def chat_stream(request: Request):
    check_key(request)
    
    # 가장 최근 user 메시지 가져오기
    user_last = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            user_last = m.get("content", "")
            break

    # 전세 체크리스트 트리거
    trigger_keywords = ["체크리스트", "확인할 사항", "확인 사항", "계약 전", "조심", "주의", "예방"]
    if '전세' in user_last and any(keyword in user_last for keyword in trigger_keywords):
        reply_text = JEONSE_CHECKLIST
    else:
        reply_text = chat_with_gemini(user_last)

    return JSONResponse({"reply": reply_text})