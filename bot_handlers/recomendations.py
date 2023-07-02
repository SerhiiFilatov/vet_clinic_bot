"""
Получить рекомендации
"""

from aiogram import Router, Bot, F
from aiogram.filters import Text, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import data
from bot_utils import check_dialogflow_connection
from bot_keyboards import callback_keyboards as keyboard
from bot_filters import my_admin_filter


router: Router = Router()


@router.callback_query(Text("recomendations"))
async def process_start_consultation(callback: CallbackQuery):
    await callback.message.edit_text(data.VIRTUAL_ASSISTANT)


@router.message(my_admin_filter, ~StateFilter('wait_for_support_message'),
                ~StateFilter('answer_message'), ~StateFilter('wait_for_title'))
async def process_asc_bot(message: Message):
    df = await check_dialogflow_connection(text=message.text)
    if df.startswith('ERROR'):
        await message.answer(text=data.CANT_RESOLVE,
                             reply_markup=keyboard.question_for_doctor(type_of_message='question'))
    else:
        await message.answer(message.text)


@router.callback_query(keyboard.SupportCallback2.filter(F.type_of_message == "question"))
async def process_send_question_to_support(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.message.answer('Напишіть ваше запитання.')
    await state.set_state("wait_for_support_message")
    await state.update_data(second_id=int(callback_data.user_id))


@router.message(StateFilter('wait_for_support_message'))
async def process_get_support_message(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    await message.answer("Лікар отримав ваше запитання і незабаром відповість!)", reply_markup=keyboard.menu_exit)
    await bot.send_message(state_data['second_id'], f"Какой-то уебок оставил сообщение:\n--{message.text}--",
                           reply_markup=keyboard.doctors_answer(user_id=message.from_user.id))
    await state.clear()


@router.callback_query(keyboard.SupportCallback2.filter(F.type_of_message == "answer"))
async def process_confirm_answer_for_user(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer("ану дай ответку")
    await state.set_state("answer_message")
    await state.update_data(client_id=int(callback_data.user_id))


@router.message(StateFilter('answer_message'))
async def process_send_answer(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    client_id = state_data['client_id']
    await bot.send_message(client_id, f"Вітаю, з приводу Вашого запитання!:\n--{message.text}--")
    await message.answer(f'Відповідь {client_id} надіслано!')
    await state.clear()