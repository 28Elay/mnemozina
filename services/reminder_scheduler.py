import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import time
from db.local_storage import get_due_tasks, setting

fired_tasks = set()

def notify_user(task):
    from telegram_notifier import send_telegram_notification
    
    title = task["title"]
    description = task.get("description", "")
    
    sent = send_telegram_notification(title, description)
    
    if not sent:
        try:
            import subprocess
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime] > $null
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>Мнемозина</text><text>{title}</text></binding></visual></toast>")
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Мнемозина').Show($toast)
            """
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                creationflags=0x08000000
            )
        except Exception as e:
            print(f"Не удалось отправить уведомление: {e}")

def scheduler_loop():
    print("🤖 Планировщик запущен...")
    while True:
        try:
            due_tasks = get_due_tasks()
            for task in due_tasks:
                task_id = task["id"]
                if task_id not in fired_tasks:
                    fired_tasks.add(task_id)
                    print(f"⏰ Напоминание: {task['title']}")
                    notify_user(task)
        except Exception as e:
            print(f"Ошибка в планировщике: {e}")
        
        time.sleep(30)

def start_scheduler():
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    return thread