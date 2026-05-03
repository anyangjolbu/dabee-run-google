import requests
from app.core.config import get_settings

settings = get_settings()

def send_message(telegram_id: str, text: str) -> bool:
    if not settings.telegram_bot_token:
        print(f"Skip sending to {telegram_id}: No Telegram bot token")
        return False
        
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": telegram_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram API Error: {e}")
        return False
