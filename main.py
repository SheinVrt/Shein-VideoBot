from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import yt_dlp
import logging
import asyncio
import os
import requests
from datetime import datetime

# Конфигурация бота
TOKEN = os.getenv("TELEGRAM_TOKEN")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 МБ
GREETING = """Привет! Shein Media Downloader скачает твою хуйню (но не TikTok, пока не научился) абсолтно фри бесплатно (скажи спасибо)

Просто отправь мне ссылку на видео (YouTube, Instagram, VK), и я скачаю его."""

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Клавиатура с кнопкой "Начать"
start_keyboard = ReplyKeyboardMarkup(
keyboard=[[KeyboardButton(text="▶️ Начать")]],
resize_keyboard=True,
one_time_keyboard=True
)

def is_working_time():
"""Проверка времени работы (07:00-23:00 UTC)"""
hour = datetime.utcnow().hour
return 7 <= hour < 23

async def get_video_info(url: str) -> dict:
ydl_opts = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'force_ipv4': True,
    'socket_timeout': 30,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://vk.com/' if 'vk.com' in url.lower() else None
    },
    'extractor_args': {'vk': {'skip_auth': True}}
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Определение размера файла
        filesize = info.get('filesize') or 0
        if not filesize:
            try:
                response = requests.head(info['url'], timeout=10)
                filesize = int(response.headers.get('Content-Length', 0))
            except:
                filesize = 0
        
        return {
            'url': info['url'],
            'filesize': filesize,
            'format': info.get('ext', 'mp4').upper(),
            'bitrate': info.get('tbr', info.get('abr', 0))
        }
        
except Exception as e:
    raise ValueError(f"Ошибка получения данных: {str(e)}")

@dp.message(Command("start"))
@dp.message(lambda m: m.text == "▶️ Начать")
async def cmd_start(message: types.Message):
if not is_working_time():
    await message.answer("⏸ Сейчас ночной режим (бот спит)\nДоступен с 07:00 до 23:00", reply_markup=start_keyboard)
    return

await message.answer(GREETING, reply_markup=start_keyboard)

@dp.message(lambda m: m.text and m.text.startswith(('http://', 'https://')))
async def handle_links(message: types.Message):
if not is_working_time():
    await message.answer("😴 Сейчас ночной режим работы\nПопробуй с 07:00 до 23:00")
    return

url = message.text
loading_msg = await message.answer("🔍 Анализирую ссылку...")

try:
    # Блокировка TikTok
    if any(d in url.lower() for d in ['tiktok.com', 'vm.tiktok.com']):
        raise ValueError("🚫 Пока не умею скачивать TikTok (но я учусь!)")

    video_info = await get_video_info(url)
    
    # Форматирование информации о размере
    size_info = "неизвестно" if video_info['filesize'] == 0 else f"{video_info['filesize'] // 1024 // 1024} МБ"
    
    # Проверка размера (если размер известен)
    if video_info['filesize'] > MAX_FILE_SIZE:
        raise ValueError(f"📁 Слишком жирное видео ({size_info} > 50 МБ)")
        
    meta = (
        f"📦 Размер: {size_info}\n"
        f"🎞 Формат: {video_info['format']}\n"
        f"🔊 Битрейт: {video_info['bitrate']:.1f} кбит/с\n\n"
        f"Скачано через Shein Media Downloader (скажи спасибо)"
    )

    await message.answer_video(
        video_info['url'],
        caption=meta,
        supports_streaming=True
    )

except Exception as e:
    await message.answer(
        f"❌ Не вышло:\n{str(e)}\n\nПопробуй другую ссылку, братик",
        reply_markup=start_keyboard
    )

finally:
    try:
        await bot.delete_message(message.chat.id, loading_msg.message_id)
    except:
        pass

async def main():
await dp.start_polling(bot)

if __name__ == "__main__":
logging.basicConfig(level=logging.INFO)
asyncio.run(main())
