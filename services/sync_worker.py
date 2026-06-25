import requests,subprocess,threading,time
from db.local_storage import sync_rows,clear_sync,setting

API="http://127.0.0.1:8000/api/sync"

def online():
    try:
        requests.get("https://1.1.1.1",timeout=3,verify=False)
        return True
    except:
        return False

def sync_loop():
    while True:
        try:
            if online():
                rows=sync_rows()
                if rows:
                    r=requests.post(
                        API,
                        json={
                            "device_token":setting("device_token"),
                            "changes":[dict(x) for x in rows]
                        },
                        timeout=10
                    )
                    if r.ok:
                        clear_sync()
        except:
            pass
        time.sleep(30)

def start_sync():
    threading.Thread(target=sync_loop,daemon=True).start()

def call_guardian():
    tel=setting("guardian_phone")
    if not tel:
        return
    try:
        subprocess.Popen(
            f"start tel:{tel}",
            shell=True,
            creationflags=0x08000000
        )
    except:
        pass