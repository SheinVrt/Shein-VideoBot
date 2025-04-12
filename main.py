from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import os

# Настройка бота
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🤖 Shein Downloader работает! Отправь мне ссылку")

@dp.message()
async def download(message: types.Message):
    await message.answer("⏳ Скачиваю видео...")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())