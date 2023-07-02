from contextlib import suppress

from aiogram import Router, Bot, F
from aiogram.filters import Text, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot_keyboards import callback_keyboards as keyboard
from bot_database.database import Database
from bot_database.FSM import FsmChooseQuantForm
from bot_filters import ComparisonFilter
from data import user_data

router: Router = Router()


@router.callback_query(Text("store"))
async def list_categories(callback: CallbackQuery, state: FSMContext, request: Database,
                          category: str | None = None, item_id: str | None = None):
    category = await request.get_categories()
    await callback.message.edit_text(text='test1', reply_markup=keyboard.categories_keyboard(categories=category))


async def list_items(callback: CallbackQuery, state: FSMContext, request: Database,
                     category, item_id: str | None = None):
    items = await request.get_items(category)
    await callback.message.edit_text(text='test2',
                                     reply_markup=keyboard.items_list_keyboard(category=category, items=items))


async def show_item(callback: CallbackQuery, state: FSMContext, request: Database, category,  item_id):
    info = await request.get_info_about_item(int(item_id))
    await callback.message.edit_text(text=f'<pre>{info["title"]}\n'
                                          f'Ціна: {info["price"]} грн.\n'
                                          f'В наявності: {info["quantity"]}.</pre>',
                                     reply_markup=keyboard.item_keyboard(category, item_id))
    user_data[callback.from_user.id] = 0
    await state.clear()


async def choose_item(callback: CallbackQuery, state: FSMContext, request: Database, category,  item_id, new_value=0):
    info = await request.get_info_about_item(int(item_id))
    await state.set_state(FsmChooseQuantForm.value)
    await state.update_data(value=new_value)
    await state.update_data(price=info['price'])
    await state.update_data(title=info['title'])
    await state.update_data(item_id=info['id'])
    datafsm = await state.get_data()
    if datafsm['value'] > info['quantity'] or info['quantity'] <= 0:
        await callback.answer(f'Нажаль кількість товару обмежена або відсутня у продажу(', show_alert=True)
    else:
        await callback.message.edit_text(text=f'<pre>{info["title"]}\nЗамовлено: {new_value}</pre>',
                                         reply_markup=keyboard.choose_item_keyboard(category, item_id))
        print(new_value)


@router.callback_query(keyboard.NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(callback: CallbackQuery, state: FSMContext,
                                   callback_data: keyboard.NumbersCallbackFactory, request: Database):
    info = await request.get_info_about_item(int(callback_data.item_id))
    user_value = user_data.get(callback.from_user.id, 0)
    user_data[callback.from_user.id] = user_value + callback_data.value
    await state.update_data(value=user_data[callback.from_user.id])
    datafsm = await state.get_data()
    if datafsm['value'] > info['quantity'] or info['quantity'] <= 0 or datafsm['value'] <= 0:
        await callback.answer(f'В наявності лише {info["quantity"]}', show_alert=True)
        user_data[callback.from_user.id] = 0
        await state.update_data(value=user_data[callback.from_user.id])
        await update_num_text_fab(callback.message, state, user_data[callback.from_user.id],
                                  callback_data.category, callback_data.item_id, info)
        await callback.answer()
    else:
        await update_num_text_fab(callback.message, state, user_value + callback_data.value,
                                  callback_data.category, callback_data.item_id, info)
        await callback.answer()


async def update_num_text_fab(message: Message, state: FSMContext, new_value: int, category, item_id, info):
    with suppress(TelegramBadRequest):
        await message.edit_text(text=f'<pre>{info["title"]}\nДодано у кошик: {new_value}</pre>',
                                reply_markup=keyboard.choose_item_keyboard(category, item_id))
        print(new_value)


# Нажатие на кнопку "подтвердить"
@router.callback_query(keyboard.NumbersCallbackFactory.filter(F.action == "finish"), ComparisonFilter(comparison_value=0))
async def callbacks_num_finish_fab(callback: CallbackQuery, state: FSMContext, request: Database):
    datafsm = await state.get_data()
    print(datafsm)
    total_price = datafsm['value'] * datafsm['price']
    await request.add_order(user_id=callback.from_user.id, price=total_price,
                            quantity=datafsm['value'], title=datafsm['title'], status=1)
    await request.update_change_quantity(order_quantity=datafsm['value'], item_id=datafsm['item_id'])
    order_info = await request.get_order_info(callback.from_user.id)
    table_text = f"{'№': <5} {'Назва': <9} {'Ціна': <6} {'Кількість': <5}\n"
    table_text += "-" * 32 + "\n"
    for row in order_info:
        order_num, order_title, order_price, order_quantity = row[:4]
        table_text += f"{order_num: <5} {order_title: <10} {order_price: <9} {order_quantity: <4}|\n"
        table_text += "-" * 32 + "\n"
    await callback.message.edit_text(f"<pre>Ваші замовлення:\n{table_text}</pre>\n"
                                     f"Your order is waiting for you at Kyiv, Chornovola street.",
                                     reply_markup=keyboard.menu_exit)
    await state.clear()
    await callback.answer()


# SEARCH BLOCK
@router.callback_query(Text('search'))
async def search_item_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='enter the title of the medicine')
    await state.update_data(call_id=callback.message.message_id)
    await state.set_state('wait_for_title')


@router.message(StateFilter('wait_for_title'))
async def search_item(message: Message, request: Database, state: FSMContext, bot: Bot):
    call_id = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=call_id['call_id'])
    result = await request.get_find_medicine(message.text)
    if result:
        await message.answer(text=f'<pre><b>{result["title"]}</b>\n'
                                  f'Ціна: {result["price"]} грн.\n'
                                  f'В наявності: {result["quantity"]} штук.</pre>',
                             reply_markup=keyboard.item_keyboard(category=result['category'], item_id=result['id']))
    else:
        await message.answer('ничего нет', reply_markup=keyboard.search())
    await state.clear()


@router.callback_query(keyboard.BuyProductCallback.filter())
async def navigate(call: CallbackQuery, request: Database, callback_data: dict, state: FSMContext):
    callback_data = dict(callback_data)
    current_level = str(callback_data.get("level"))
    category = str(callback_data.get("category"))
    item_id = str(callback_data.get("item_id"))
    levels = {
        "0": list_categories,
        "1": list_items,
        "2": show_item,
        "3": choose_item
    }
    current_level_function = levels[current_level]
    await current_level_function(
        call,
        state,
        request,
        category=category,
        item_id=item_id
    )