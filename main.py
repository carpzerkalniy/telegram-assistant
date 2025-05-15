from fastapi import FastAPI, Request
import os
import httpx

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot7259946019:AAHQ61Dwp_GuXuvAPaoXF_6ea8NQNSZW2EA"


@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        async with httpx.AsyncClient() as client:
            await client.post(f"{API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"Ты сказал: {text}"
            })

    return {"ok": True}
