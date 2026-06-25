import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
import winsound
import ctypes
import glob
from db.local_storage import get_due_tasks

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sounds")

fired_tasks = set()

def get_sound_file():
    if not os.path.exists(SOUNDS_DIR):
        os.makedirs(SOUNDS_DIR)
        print(f"Папка sounds создана: {SOUNDS_DIR}")
        return None
    
    wav_files = glob.glob(os.path.join(SOUNDS_DIR, "*.wav"))
    
    if wav_files:
        print(f"Найден звуковой файл: {wav_files[0]}")
        return wav_files[0]
    
    print("WAV файлы не найдены в папке sounds")
    return None

def play_alarm():
    sound_file = get_sound_file()
    
    if sound_file:
        try:
            print(f"Воспроизведение: {sound_file}")
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            time.sleep(2)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            play_default_sound()
    else:
        play_default_sound()

def play_default_sound():
    print("Стандартный звук winsound")
    for _ in range(3):
        winsound.Beep(1000, 500)
        time.sleep(0.2)

def show_alert(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)

def send_telegram_notification(title, description=""):
    try:
        import requests
        bot_token = os.getenv("TG_BOT_TOKEN")
        chat_id = os.getenv("TG_CHAT_ID")
        if not bot_token or not chat_id:
            return False
        url = f"{bot_token}"
        msg = f" <b>{title}</b>"
        if description:
            msg += f"\n\n<i>{description}</i>"
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Ошибка Telegram: {e}")
        return False

def notify_user(task):
    title = task["title"]
    description = task.get("description", "Пора выполнить задачу!")

    play_alarm()

    threading.Thread(target=show_alert, args=(title, description), daemon=True).start()

    send_telegram_notification(title, description)

    print(f"Напоминание: {title}")

def scheduler_loop():
    print("Планировщик запущен...")
    while True:
        try:
            due_tasks = get_due_tasks()
            for task in due_tasks:
                task_id = task["id"]
                if task_id not in fired_tasks:
                    fired_tasks.add(task_id)
                    notify_user(task)
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(30)

def start_scheduler():
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    start_scheduler()
    print("Планировщик работает. Ctrl+C для остановки.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Остановлено.")