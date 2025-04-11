import os
import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Формируем психологический промпт
def create_prompt(user_input):
    return f"""
Ты — опытный детский психолог. Твоя задача — поддержать ребёнка, который попал в трудную жизненную ситуацию.
Говори на простом, добром и понятном русском языке. Отвечай мягко, с заботой и уважением.
Помогай понять чувства, поддерживай и не осуждай.

Если ребёнок пишет о насилии, страхе, тревоге — успокой его, объясни, что он не виноват, и предложи обратиться за помощью к родителям, учителю, школьному психологу или взрослому, которому он доверяет.

Вот сообщение ребёнка:
\"\"\"{user_input}\"\"\"
"""

# Отправка запроса к OpenRouter API
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
        "model": "mistralai/mistral-7b-instruct",  # Можешь заменить на любую другую доступную
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            elif "error" in data:
                return f"⚠️ Ошибка: {data['error'].get('message', 'Неизвестная ошибка')}"
            else:
                return "⚠️ Прости, я не смог ответить. Попробуй чуть позже."

# /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я твой добрый психолог-бот 🤗\n"
        "Ты можешь рассказать мне, что тебя тревожит, и я постараюсь поддержать."
    )

# Ответ на обычные сообщения
@dp.message()
async def handle_message(message: Message):
    user_text = message.text
    await message.answer("Думаю... 💭")
    response = await ask_openrouter(user_text)
    await message.answer(response)

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
