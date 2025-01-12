from aiogram.fsm.state import State, StatesGroup

class ProfileUser(StatesGroup):
	user_weight = State()
	user_height = State()
	user_age = State()
	user_action_time = State()
	user_city = State()
	user_obj_calories = State()


class LoggingFood(StatesGroup):
	food_eat_weight = State()