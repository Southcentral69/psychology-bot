import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram import Router
from aiogram.utils.markdown import hbold
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN is not set.")
if OPENROUTER_API_KEY is None:
    raise ValueError("OPENROUTER_API_KEY is not set.")

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

@router.message(commands=["start"])
async def start_handler(message: Message):
    await message.answer("Привет! Я твой психолог-бот 🧠\nМожешь рассказать мне, что тебя тревожит — я постараюсь помочь.")

@router.message()
async def handle_message(message: Message):
    await message.answer("Я думаю... ⏳")
    response = await ask_openrouter(message.text)
    await message.answer(response)

async def ask_openrouter(user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "openchat/openchat-3.5",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный психолог, который общается с детьми. Отвечай просто, понятно и по-доброму."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        async with ClientSession() as session:
            async with session.post(url, headers=headers, json=json_data) as resp:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.exception("Ошибка при обращении к OpenRouter")
        return "⚠️ Ошибка: Не удалось получить ответ от ИИ."

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
