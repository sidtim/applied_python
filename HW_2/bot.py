import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command

from config import TOKEN
from handlers import daily_norm_calories, logging_activity
from middlewares.middleware import LoggingMiddleware

sys.path.append("..")


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
        # parse_mode=ParseMode.MARKDOWN_V2
    ),
)
# Диспетчер
dp = Dispatcher()
# Подключение роутера
dp.include_routers(daily_norm_calories.router, logging_activity.router)
dp.message.middleware(LoggingMiddleware())


# Запуск процесса полинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
