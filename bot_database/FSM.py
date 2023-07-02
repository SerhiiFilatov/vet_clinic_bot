from aiogram.filters.state import State, StatesGroup


class FsmForm(StatesGroup):
    stage = State()
    date = State()
    time = State()
    pet: str = State()
    problem: str = State()


class FsmDocCallForm(StatesGroup):
    pet_dc: str = State()
    date_dc = State()
    time_dc = State()
    adress_dc = State()
    phone_number_dc = State()
    problem_dc: str = State()


class FsmChooseQuantForm(StatesGroup):
    value: int = State()
    price: int = State()
    title: str = State()