import data
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot_database.FSM import FsmChooseQuantForm


class MessageSizeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if 3 <= len(message.text) <= 100:
            return True
        else:
            await message.answer("Опишіть проблему не меньше ніж 10 і не більш ніж 100 символами")
        return False


def my_admin_filter(message: Message) -> bool:
    if message.from_user.id in data.admin_list.id.values():
        return False
    else:
        return True


class ComparisonFilter(BaseFilter):
    comparison_value= 'comparison_value'

    def __init__(self, comparison_value: int):
        self.expected_value = comparison_value

    async def __call__(self, callback: CallbackQuery, state: FSMContext) -> bool:
        datafsm = await state.get_data()
        if 'value' in datafsm:
            return datafsm['value'] is not None and datafsm['value'] > self.expected_value
        else:
            return True