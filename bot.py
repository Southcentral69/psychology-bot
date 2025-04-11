import os
print("TELEGRAM_TOKEN =", os.getenv("TELEGRAM_TOKEN"))

import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# Получаем переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Проверка на наличие токенов
if TELEGRAM_TOKEN is None:
    raise ValueError("❌ Переменная TELEGRAM_TOKEN не найдена.")
if OPENROUTER_API_KEY is None:
    raise ValueError("❌ Переменная OPENROUTER_API_KEY не найдена.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Формируем промпт для психолога
def create_prompt(user_input):
    return f"""
Ты — опытный детский психолог. Твоя задача — поддержать ребёнка, который попал в трудную ситуацию.
Говори добрым, простым языком. Успокой, поддержи, не осуждай.
Если ребёнок упоминает насилие или страх — скажи, что он не виноват, и предложи обратиться к взрослым, которым он доверяет.

Сообщение ребёнка:
\"\"\"{user_input}\"\"\"
"""

# Отправка запроса к OpenRouter
async def ask_openrouter(message_text: str) -> str:
    prompt = create_prompt(message_text)
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Southcentral69/psychology-bot",
        "X-Title": "telegram-psychology-bot"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",  # бесплатная и нормальная модель
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            elif "error" in data:
                return f"⚠️ Ошибка: {data['error'].get('message', 'Неизвестная ошибка')}"
            else:
                return "⚠️ Прости, не смог ответить. Попробуй позже."

# Команда /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я твой психолог-бот 🧠\n"
        "Можешь рассказать мне, что тебя тревожит — я постараюсь помочь."
    )

# Обработка всех сообщений
@dp.message()
async def handle_message(message: Message):
    user_text = message.text
    await message.answer("Я думаю... 💭")
    response = await ask_openrouter(user_text)
    await message.answer(response)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
