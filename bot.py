
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram import Router
import aiohttp
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я — психологический бот. Расскажи, что у тебя случилось, и я постараюсь помочь.")

@router.message()
async def handle_message(message: Message):
    user_text = message.text
    await message.answer("Я думаю... ⏳")
    try:
        response = await ask_openrouter(f"Ты — детский психолог. Ответь ребёнку в дружелюбной форме на: {user_text}")
        await message.answer(response)
    except Exception as e:
        await message.answer("⚠️ Ошибка: Не удалось получить ответ от ИИ.")

async def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/mistral",  # можно поменять на другой
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

if __name__ == "__main__":
    import asyncio
    from aiogram import F
    from aiogram.types import Update

    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())
