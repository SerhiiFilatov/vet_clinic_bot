from aiogram import Router, Bot

from aiogram.filters import CommandStart, Text
from aiogram.types import CallbackQuery, Message, BotCommand
from aiogram.fsm.context import FSMContext

import data
from bot_keyboards import callback_keyboards as keyboard



router: Router = Router()


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Старт'),
        ]
    await bot.set_my_commands(main_menu_commands)


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(text=data.GREETING, reply_markup=keyboard.keyboard_builder(width=1, **data.BUTTONS_INFO))
    await state.clear()


@router.callback_query(Text("exit"))
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='прихабарся на дорожку',
                                     reply_markup=keyboard.keyboard_builder(width=1, **data.BUTTONS_INFO))
    await state.clear()





