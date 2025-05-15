from fastapi import Request
from google_calendar import add_event, get_upcoming_events
import datetime
import re
import httpx
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Упрощённый парсер для "завтра в 14:00"
def parse_datetime(text):
    now = datetime.datetime.now()
    match = re.search(r"(сегодня|завтра)?\s*в\s*(\d{1,2})(?::(\d{2}))?", text, re.IGNORECASE)
    if match:
        day, hour, minute = match.groups()
        minute = int(minute) if minute else 0
        if day == "завтра":
            base = now + datetime.timedelta(days=1)
        else:
            base = now
        dt = datetime.datetime(base.year, base.month, base.day, int(hour), minute)
        return dt
    return None

async def handle_addevent(chat_id: int, text: str):
    time = parse_datetime(text)
    if not time:
        await send_message(chat_id, "Не смог понять дату. Попробуй: /addevent Встреча завтра в 15:00")
        return

    # Вырезаем название события (всё до даты)
    summary = text.split("в")[0].replace("/addevent", "").strip().capitalize()
    link = add_event(summary, time)
    await send_message(chat_id, f"Событие добавлено: {summary} в {time.strftime('%H:%M %d.%m')}
{link}")

async def handle_calendar(chat_id: int):
    events = get_upcoming_events()
    if not events:
        await send_message(chat_id, "Ближайших событий не найдено.")
        return

    msg = "🗓 Ближайшие события:
"
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        summary = e.get("summary", "Без названия")
        msg += f"- {start[:16].replace('T', ' ')} — {summary}\n"
    await send_message(chat_id, msg)

async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })
