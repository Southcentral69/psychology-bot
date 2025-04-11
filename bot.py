import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

# 🔐 Вставь свои ключи сюда
TELEGRAM_TOKEN = ""
OPENROUTER_API_KEY = ""

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 🧠 Русский промпт психолога
def create_prompt(user_input):
    return f"""
Ты — опытный детский психолог. Твоя задача — поддерживать ребёнка в трудной ситуации.

Говори на простом, добром и понятном русском языке. Всегда отвечай мягко, с заботой и уважением. Помогай понять чувства, поддерживай и не осуждай.

Если ребёнок говорит, что его бьют, обижают или он чувствует страх, объясни, что он не виноват, и подскажи, к кому можно обратиться (родители, школьный психолог, взрослые, которым он доверяет).

Вот сообщение от ребёнка:
\"\"\"{user_input}\"\"\"
"""

# 📡 Запрос к OpenRouter
async def ask_openrouter(message_text: str) -> str:
    prompt = create_prompt(message_text)
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",  # дешёвая и нормальная модель
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
                return "⚠️ Прости, я не смог ответить. Попробуй позже."

# Команда /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я твой добрый друг-психолог 🤗\n"
        "Ты можешь рассказать мне, что тебя тревожит, а я постараюсь поддержать и помочь."
    )

# Все остальные сообщения
@dp.message()
async def handle_message(message: Message):
    user_text = message.text
    await message.answer("Думаю... 💭")
    response = await ask_openrouter(user_text)
    await message.answer(response)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
