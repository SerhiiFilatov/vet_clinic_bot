"""
Вызов врача
"""

from environs import Env

from aiogram import Router, Bot
from aiogram.filters import Text, StateFilter
from aiogram3_calendar import simple_cal_callback, SimpleCalendar
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

import data
from bot_database.FSM import FsmDocCallForm
from bot_database.database import Database
from bot_keyboards import callback_keyboards as keyboard


env = Env()
router: Router = Router()


@router.callback_query(Text("doctors_call"))
async def process_choose_pet(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="DC Хто Ваш улюбленець?)",
                                     reply_markup=keyboard.keyboard_builder(width=3, **data.PET_LIST))
    await state.update_data(stage=callback.data)
    await state.set_state(FsmDocCallForm.pet_dc)
    datakey = await state.get_state()
    print(datakey)


@router.callback_query(StateFilter('FsmDocCallForm:pet_dc'))
async def process_start_calendar(callback: CallbackQuery, state: FSMContext):
    await state.update_data(pet_dc=callback.data)
    await state.set_state(FsmDocCallForm.date_dc)
    await callback.message.edit_text(text="DC Оберіть дату прийому ",
                                     reply_markup=await SimpleCalendar().start_calendar())


@router.callback_query(StateFilter('FsmDocCallForm:date_dc'), simple_cal_callback.filter())
async def process_simple_calendar_start_time(callback: CallbackQuery, callback_data: dict,
                                             state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)
    if selected:
        await state.update_data(date_dc=date.date().strftime('%d-%m-%Y'))
        await callback.message.edit_text(text='DC Оберіть час',
                                         reply_markup=keyboard.keyboard_builder(width=3, **data.CALL_TIME))
        await state.set_state(FsmDocCallForm.time_dc)


@router.callback_query(StateFilter('FsmDocCallForm:time_dc'))
async def process_time(callback: CallbackQuery, state: FSMContext):
    await state.update_data(time_dc=callback.data)
    await state.set_state(FsmDocCallForm.adress_dc)
    await callback.message.edit_text('Вкажіть адресу, за якою чекатимуть лікаря.')


@router.message(StateFilter('FsmDocCallForm:adress_dc'), lambda x: 3 <= len(x.text) <= 100)
async def process_adress(message: Message, state: FSMContext):
    await state.update_data(adress_dc=message.text)
    await state.set_state(FsmDocCallForm.phone_number_dc)
    await message.answer(text='Вкажіть Ваш контактний телефон', reply_markup=keyboard.phone)


@router.message(StateFilter('FsmDocCallForm:phone_number_dc'))
async def process_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number_dc=message.contact.phone_number)
    await state.set_state(FsmDocCallForm.problem_dc)
    await message.answer(data.PROBLEM)


@router.message(StateFilter('FsmDocCallForm:problem_dc'), lambda x: 3 <= len(x.text) <= 100)
async def process_all(message: Message, state: FSMContext, bot: Bot, request: Database):
    await state.update_data(problem_dc=message.text)
    datakey = await state.get_data()
    user_id = message.from_user.id
    date = datakey['date_dc']
    time = datakey['time_dc']
    pet = datakey['pet_dc']
    adress = str(datakey['adress_dc'])
    phone_number = str(datakey['phone_number_dc'])
    problem = datakey['problem_dc']
    await message.answer(f"<b>Виклик лікаря: </b>{date}\n"
                         f"<b>В {time} дня</b>\n"
                         f"<b>Адрес: </b>{adress}\n"
                         f"<b>Телефон: </b>{phone_number}\n"
                         f"<b>Тема звернення: </b>{problem}",
                         reply_markup=keyboard.menu_exit)
    await bot.send_message(chat_id=env.str('ADMIN_ID_2'), text=f'{message.from_user.username}\n'
                                                             f'{date, time}\n{pet}\n{problem}')
    await request.add_info_doc_call(id=user_id, pet=pet, date=date, time=time,
                                    problem=problem, phone_number=phone_number, adress=adress)
    await state.clear()