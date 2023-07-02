import asyncio
import asyncpg
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from bot_config import settings
from bot_keyboards import menu_button
from bot_handlers import start_exit_menu, making_an_appointment, doctors_call, recomendations, info_doctor, store
from bot_middlewares.reg_middleware import DbSessionMiddleware


async def create_pool():
    return await asyncpg.create_pool(user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
                                     host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'),
                                     database=os.getenv('DATABASE'))

# storage: RedisStorage = RedisStorage.from_url('redis://localhost:6379/0')

storage = MemoryStorage()

async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=storage)

    dp.include_router(start_exit_menu.router)
    dp.include_router(making_an_appointment.router)
    dp.include_router(doctors_call.router)
    dp.include_router(recomendations.router)
    dp.include_router(store.router)
    dp.include_router(info_doctor.router)

    await menu_button.set_main_menu(bot)

    pool_connect = await create_pool()
    dp.update.middleware.register(DbSessionMiddleware(pool_connect))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
