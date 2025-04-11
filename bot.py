import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import requests

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Проверка токенов
if not BOT_TOKEN:
    raise ValueError("❌ Переменная BOT_TOKEN не найдена в .env файле.")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ Переменная OPENROUTER_API_KEY не найдена в .env файле.")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

@dp.message_handler()
async def handle_message(message: types.Message):
    user_text = message.text.strip()

    await message.answer("Я думаю... ⏳")

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openrouter/cinematika-7b",  # бесплатная модель
            "messages": [
                {"role": "system", "content": "Ты добрый детский психолог, говори дружелюбно, мягко и понятно ребенку."},
                {"role": "user", "content": user_text}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]

        await message.answer(reply)

    except Exception as e:
        await message.answer("⚠️ Ошибка: Не удалось получить ответ от ИИ.")
        print("Ошибка OpenRouter:", e)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
