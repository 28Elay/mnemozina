from threading import Thread,Timer
from time import sleep
from db.local_storage import due_tasks
import subprocess

fired=set()

def notify(title,msg):
    try:
        ps=f"""
[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime] > $null
[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime] > $null
$xml=New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>{title}</text><text>{msg}</text></binding></visual></toast>")
$toast=[Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Мнемозина').Show($toast)
"""
        subprocess.run(
            ["powershell","-ExecutionPolicy","Bypass","-Command",ps],
            capture_output=True,
            creationflags=0x08000000
        )
    except:
        pass

def repeat(task):
    notify("Напоминание",f"Пожалуйста выполните: {task['title']}")

def loop():
    while True:
        try:
            for t in due_tasks():
                if t["id"] in fired:
                    continue
                fired.add(t["id"])
                notify("Напоминание",t["title"])
                Timer(120,lambda x=t:repeat(x)).start()
        except:
            pass
        sleep(30)

def start_scheduler():
    Thread(target=loop,daemon=True).start()