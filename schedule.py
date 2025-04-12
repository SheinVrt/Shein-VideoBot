import os
import time
from datetime import datetime

def is_working_time():
    hour = datetime.utcnow().hour
    return 7 <= hour < 23  # Работаем с 07:00 до 23:00 UTC

while True:
    if is_working_time():
        if not os.path.exists("bot_on"):
            os.system("railway up &")
            open("bot_on", "w").close()
    else:
        if os.path.exists("bot_on"):
            os.system("railway down")
            os.remove("bot_on")
    time.sleep(300)  # Проверка каждые 5 минут