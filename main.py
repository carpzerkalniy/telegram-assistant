from fastapi import FastAPI, Request
import httpx
import os
import re
from telegram_calendar_handlers import handle_addevent, handle_calendar

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.post("/webhook")
async def webhook(req: Request):
    try:
        data = await req.json()
    except Exception:
        body = await req.body()
        return {"error": "Не удалось распарсить JSON", "raw": body.decode()}

    if not isinstance(data, dict):
        return {"error": "Ожидали JSON-объект, получили другое", "raw": str(data)}

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text.startswith("/addevent"):
            await handle_addevent(chat_id, text)
        elif text.startswith("/calendar"):
            await handle_calendar(chat_id)
        elif re.search(r"(завтра|сегодня).*в\\s*\\d{1,2}", text.lower()):
            await handle_addevent(chat_id, f"/addevent {text}")
        else:
            await send_message(chat_id, f"Ты сказал: {text}")

    return {"ok": True}


async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendMessage", json={{
            "chat_id": chat_id,
            "text": text
        }})
