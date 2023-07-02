from environs import Env
from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


env = Env()


class ChooseTimeCallbackFactory(CallbackData, prefix='time', sep='|'):
    time: str


class SupportCallback(CallbackData, prefix='ask_support', sep='|'):
     messages: str
     user_id: str


class SupportCallback2(CallbackData, prefix='ask_support', sep='|'):
    user_id: str
    type_of_message: str


class BuyProductCallback(CallbackData, prefix='buy_product', sep='|'):
    level: int
    category: str
    item_id: str

class BuyItemCallback(CallbackData, prefix='buy_product', sep='|'):
    level: str
    item_id: str


def make_callback_data(level, category="0", item_id="0"):
    return BuyProductCallback(level=level, category=category, item_id=item_id).pack()


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int]
    category: str
    item_id: str


def search():
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text='🔍 Найди меня', callback_data="search"))
    kb_builder.row(InlineKeyboardButton(text='🔙 Повернутися в меню', callback_data="exit"))
    return kb_builder.as_markup()

def categories_keyboard(categories):
    CURRENT_LEVEL = 0
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for category in categories:
        button_text = f"{category}"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category)
        buttons.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    kb_builder.row(*buttons, width=2)
    kb_builder.row(InlineKeyboardButton(text='🔍 Найди меня', callback_data="search"))
    kb_builder.row(InlineKeyboardButton(text='🔙 Повернутися в меню', callback_data="exit"))
    return kb_builder.as_markup()


def items_list_keyboard(category, items):
    CURRENT_LEVEL = 1
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for item in items:
        button_text = f"{item[1]}"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category, item_id=item[0])
        buttons.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    kb_builder.row(*buttons, width=2)
    kb_builder.row(InlineKeyboardButton(text='🔙 Назад',
                                        callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category=category)))
    return kb_builder.as_markup()


def item_keyboard(category, item_id):
    CURRENT_LEVEL = 2
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    kb_builder.row(InlineKeyboardButton(text='Замовити',
                                        callback_data=BuyProductCallback(level=3, category=category,
                                                                      item_id=item_id).pack()))

    kb_builder.row(InlineKeyboardButton(text='🔙 Назад',
                                        callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category=category)))
    return kb_builder.as_markup()


def choose_item_keyboard(category, item_id):
    CURRENT_LEVEL = 3
    builder = InlineKeyboardBuilder()
    builder.button(text="-1",
                   callback_data=NumbersCallbackFactory(action="change", value=-1, category=category, item_id=item_id))
    builder.button(text="Підтвердити",
                   callback_data=NumbersCallbackFactory(action="finish", category=category, item_id=item_id))
    builder.button(text="+1",
                   callback_data=NumbersCallbackFactory(action="change", value=+1, category=category, item_id=item_id))
    builder.button(text='🔙 Назад',
                   callback_data=make_callback_data(level=CURRENT_LEVEL - 1, category=category, item_id=item_id))

    builder.adjust(3)
    return builder.as_markup()


def question_for_doctor(type_of_message, user_id: str | None = None):
    if user_id:
        contact_id = str(user_id)
    else:
        contact_id = env.str('ADMIN_ID_2')
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text='Залишити запитання', callback_data=SupportCallback2(type_of_message=type_of_message,
                                                                               user_id=contact_id).pack()),
        InlineKeyboardButton(text='🔙 Повернутися в меню', callback_data="exit")
    ]
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup()


def doctors_answer(user_id):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text='Ответ',
                                                                callback_data=SupportCallback2(
                                                                    type_of_message='answer',
                                                                    user_id=user_id).pack())]
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def keyboard_builder(width: int, last_btn: str | None = None, **kwargs) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for text, callback in kwargs.items():
        buttons.append(InlineKeyboardButton(text=text, callback_data=callback))
    kb_builder.row(*buttons, width=width)
    if last_btn:
        kb_builder.row(InlineKeyboardButton(text=last_btn, callback_data='last_btn'))
    return kb_builder.as_markup()


def get_time_keyboard(width=2, **kwargs) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for text, callback in kwargs.items():
        buttons.append(InlineKeyboardButton(text=text, callback_data=ChooseTimeCallbackFactory(time=callback).pack()))
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()


menu_exit: InlineKeyboardButton = InlineKeyboardButton(text='🔙 Повернутися в меню', callback_data="exit")
menu_exit = InlineKeyboardMarkup(inline_keyboard=[[menu_exit]])

phone: InlineKeyboardButton = KeyboardButton(text='☎ Поділитись номером',request_contact=True)
phone = ReplyKeyboardMarkup(keyboard=[[phone]], resize_keyboard=True)