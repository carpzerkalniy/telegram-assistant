import datetime
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds_data = os.getenv("GOOGLE_CREDENTIALS")
    token_data = os.getenv("GOOGLE_TOKEN")

    if not creds_data or not token_data:
        raise Exception("Не найдены переменные окружения GOOGLE_CREDENTIALS или GOOGLE_TOKEN")

    creds_json = json.loads(token_data)
    creds = Credentials.from_authorized_user_info(creds_json, SCOPES)
    return build("calendar", "v3", credentials=creds)




def add_event(summary: str, start_time: datetime.datetime, duration_minutes=60):
    service = get_calendar_service()
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)
    
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Europe/Moscow'},
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get("htmlLink")

def get_upcoming_events(max_results=5):
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events
