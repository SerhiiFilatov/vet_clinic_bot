from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

import data
from bot_keyboards import callback_keyboards as keyboard

router: Router = Router()


@router.callback_query(Text("doctor"))
async def process_choose_pet(callback: CallbackQuery):
    await callback.message.edit_text(data.WARNING, reply_markup=keyboard.menu_exit)