import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_telegram_notification(title, description=""):
    bot_token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("⚠️  Telegram не настроен: проверьте .env файл")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    msg = f"🔔 <b>{title}</b>"
    if description:
        msg += f"\n\n<i>{description}</i>"
    msg += "\n\n⏰ Пора выполнить эту задачу!"

    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Уведомление отправлено: {title}")
            return True
        else:
            print(f"❌ Ошибка Telegram API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False