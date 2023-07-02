"""
Запись на прием в клинику
"""
from environs import Env

from aiogram import Router, F, Bot
from aiogram3_calendar import simple_cal_callback, SimpleCalendar
from aiogram.filters import Text, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import data
from bot_utils import date_time_dict
from bot_keyboards import callback_keyboards as keyboard
from bot_database.database import Database
from bot_database.FSM import FsmForm


router: Router = Router()


@router.callback_query(Text("appointment"))
async def process_choose_pet(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Хто Ваш улюбленець?)",
                                     reply_markup=keyboard.keyboard_builder(width=3, **data.PET_LIST))
    await state.update_data(stage=callback.data)
    await state.set_state(FsmForm.pet)


@router.callback_query(StateFilter('FsmForm:pet'), F.data.in_({'cat', 'bird', 'dog'}))
async def process_start_calendar(callback: CallbackQuery, state: FSMContext):
    await state.update_data(pet=callback.data)
    await state.set_state(FsmForm.date)
    await callback.message.edit_text(text="Оберіть дату прийому ",
                                     reply_markup=await SimpleCalendar().start_calendar())


@router.callback_query(StateFilter('FsmForm:date'), simple_cal_callback.filter())
async def process_simple_calendar_start_time(callback: CallbackQuery, callback_data: dict,
                                             state: FSMContext, request: Database):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        await state.update_data(date=date.date().strftime('%d-%m-%Y'))
        datakey = await state.get_data()
        date = datakey['date']
        time = await request.get_time(date)
        available_times = [t for t in data.TIME if t not in time]
        reply_markup = keyboard.get_time_keyboard(**date_time_dict(available_times))
        await callback.message.edit_text(text='Оберіть час', reply_markup=reply_markup)
        await state.set_state(FsmForm.time)


@router.callback_query(StateFilter('FsmForm:time'), keyboard.ChooseTimeCallbackFactory.filter())
async def process_problem(callback: CallbackQuery, state: FSMContext):
    await state.update_data(time=callback.data)
    await state.set_state(FsmForm.problem)
    await callback.message.edit_text(data.PROBLEM)


@router.message(StateFilter('FsmForm:problem'), lambda x: 3 <= len(x.text) <= 100)
async def process_all(message: Message, state: FSMContext, bot: Bot, request: Database):
    env = Env()
    await state.update_data(problem=message.text)
    datakey = await state.get_data()
    user_id = message.from_user.id
    date = datakey['date']
    time = datakey['time'].split('|')[1]
    pet = datakey['pet']
    problem = datakey['problem']
    await message.answer(f"<b>Ми чекаємо на вас та вашого глистоносця:</b> {date}\n"
                         f"<b>О {time} годині.</b>\n"
                         f"<b>За адресою: вул. Козломордая, 100500</b>\n"
                         f"<b>Контактний телефон:</b> <code>+38000000000</code> \n\n"
                         f"<b>Тема звернення:</b> {problem}",
                         reply_markup=keyboard.menu_exit)
    await bot.send_message(chat_id=env.str('ADMIN_ID_2'), text=f'{message.from_user.username}\n'
                                                             f'{date, time}\n{pet}\n{problem}')
    await request.add_info(id=user_id, pet=pet, date=date, time=time, problem=problem)
    await state.clear()
