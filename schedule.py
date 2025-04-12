import os
import time
from datetime import datetime

def should_be_active():
    hour = datetime.utcnow().hour
    return 7 <= hour < 23  # Работаем с 07:00 до 23:00 UTC

while True:
    if should_be_active():
        if not os.path.exists("bot_active"):
            os.system("railway up &")
            open("bot_active", "w").close()
            print("🟢 Бот включен")
    else:
        if os.path.exists("bot_active"):
            os.system("railway down")
            os.remove("bot_active")
            print("🔴 Бот выключен на ночь")
    time.sleep(300)  # Проверка каждые 5 минут
