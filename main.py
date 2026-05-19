import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

SYSTEM_PROMPT = """Eres un asistente virtual del profesor Andrés, experto en enseñanza de inglés. 
Tu trabajo es atender consultas de estudiantes y personas interesadas en aprender inglés.
Responde siempre en español de manera amable y profesional."""

async def ask_openai(user_message: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 500
            },
            timeout=30.0
        )
        data = response.json()
        if "choices" not in data:
            return "Lo siento, hubo un error técnico. Intenta de nuevo."
        return data["choices"][0]["message"]["content"]

async def send_whatsapp_message(to: str, message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages",
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": message}
            },
            timeout=30.0
        )
        print(f"WhatsApp response: {response.status_code} - {response.text}")

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return JSONResponse(content=int(params.get("hub.challenge", 0)))
    return JSONResponse(content={"error": "token inválido"}, status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            if message["type"] == "text":
                user_text = message["text"]["body"]
                response_text = await ask_openai(user_text)
                await send_whatsapp_message(from_number, response_text)
    except Exception as e:
        print(f"Error: {e}")
    return JSONResponse(content={"status": "ok"})

@app.get("/")
async def root():
    return {"status": "Bot inglés activo"}
