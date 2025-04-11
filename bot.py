import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils import executor
import aiohttp

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Проверка наличия токенов
if TELEGRAM_TOKEN is None:
    raise ValueError("TELEGRAM_TOKEN is not set")
if OPENROUTER_API_KEY is None:
    raise ValueError("OPENROUTER_API_KEY is not set")

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Обработка команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я твой психолог-бот \U0001F9E0\n"
                         "Можешь рассказать мне, что тебя тревожит — я постараюсь помочь.")

# Основной обработчик текста
@dp.message()
async def handle_message(message: Message):
    user_message = message.text
    await message.answer("Я думаю... \u231B")

    try:
        # Отправка запроса к OpenRouter
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            json_data = {
                "model": "openchat/openchat-3.5-0106",
                "messages": [
                    {"role": "system", "content": "Ты дружелюбный психолог, разговаривающий с ребёнком."},
                    {"role": "user", "content": user_message}
                ]
            }
            async with session.post("https://openrouter.ai/api/v1/chat/completions",
                                    headers=headers, json=json_data) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"]
                    await message.answer(reply)
                else:
                    await message.answer(f"\u26A0\ufe0f Ошибка: OpenRouter вернул статус {resp.status}")
    except Exception as e:
        logging.exception("Ошибка при запросе к OpenRouter")
        await message.answer(f"\u26A0\ufe0f Ошибка: {str(e)}")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
