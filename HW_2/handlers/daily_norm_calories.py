from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters import (UserActionTimeFilter, UserAgeFilter, UserHeightFilter,
                     UserObjCaloriesFilter, UserWeightFilter)
from states.state_user import ProfileUser
from utils import calc_norm_calories, calc_norm_water

router = Router()


# Хэндлер для сброса всей введенной информации о пользователе
# (например, пользователь допустил ошибку при вводе профиля и хочет ввести всю информацию заново)
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать в @TimoninAiHw2Bot для расчёта нормы воды, калорий и трекинга активности! \nДля ознакомления со всеми доступными командами введите <b>/info</b>. \nЧтобы начать работу с ботом, введите команду <b>/set_profile</b>"
    )


@router.message(Command("info"))
async def cmd_info(message: Message, state: FSMContext):
    await message.answer(
        """
/start - сброс всей ранее введенной информации о пользователе
/info - вывод информации по всем командам бота
/set_profile - настройка профиля пользователя
/log_water - логирование воды
/log_food <i>product_name</i> - логирование еды
/log_workout <i>workout_type</i> <i>workout_time</i> - логирование тренировок
/check_progress - прогресс по воде и калориям
"""
    )


# В случае отсутствия состояния (StateFilter(None)), команда /set_profile начнет работу с этого обработчика
@router.message(StateFilter(None), Command("set_profile"))
async def choose_weight(message: Message, state: FSMContext):
    await message.answer(text="Введите ваш вес (в кг):")
    await state.set_state(ProfileUser.user_weight)


@router.message(ProfileUser.user_weight, UserWeightFilter())
async def choose_height(message: Message, state: FSMContext):
    # Сохранение данных состояния пользователя в переменную при помощи state.update_data
    await state.update_data(weight=float(message.text))

    await message.answer(text="Введите ваш рост (в см):")
    await state.set_state(ProfileUser.user_height)


@router.message(ProfileUser.user_height, UserHeightFilter())
async def choose_age(message: Message, state: FSMContext):
    # Сохранение данных состояния пользователя в переменную при помощи state.update_data
    await state.update_data(height=float(message.text))

    await message.answer(text="Введите ваш возраст:")
    await state.set_state(ProfileUser.user_age)


@router.message(ProfileUser.user_age, UserAgeFilter())
async def choose_action_time(message: Message, state: FSMContext):
    # Сохранение данных состояния пользователя в переменную при помощи state.update_data
    await state.update_data(age=float(message.text))

    await message.answer(text="Сколько минут активности у вас в день?")
    await state.set_state(ProfileUser.user_action_time)


@router.message(ProfileUser.user_action_time, UserActionTimeFilter())
async def choose_city(message: Message, state: FSMContext):
    # Сохранение данных состояния пользователя в переменную при помощи state.update_data
    await state.update_data(activity=float(message.text))

    await message.answer(text="В каком городе вы находитесь?")
    await state.set_state(ProfileUser.user_city)


@router.message(ProfileUser.user_city)
async def choose_obj_calories(message: Message, state: FSMContext):
    # Сохранение данных состояния пользователя в переменную при помощи state.update_data
    await state.update_data(city=message.text.lower().title())

    await message.answer(text="Какая у вас цель по потреблению калорий в сутки?")
    await state.set_state(ProfileUser.user_obj_calories)


@router.message(ProfileUser.user_obj_calories, UserObjCaloriesFilter())
async def calc_norm_calories_water(message: Message, state: FSMContext):
    # Сохранение данных состояния пользователя в переменную при помощи state.update_data
    await state.update_data(user_obj_calories=float(message.text))
    # С помощью state.get_data() получаем словарь данных по всем переменным состояния, которые заносили через state.update_data
    data = await state.get_data()

    norm_calories = await calc_norm_calories(
        data["weight"], data["height"], data["age"], data["activity"]
    )

    norm_water = await calc_norm_water(data["weight"], data["activity"], data["city"])

    await message.answer(
        text=f"Ваша суточная норма воды: {norm_water} мл. \nВаша суточная норма каллорий: {norm_calories} ккал."
    )

    await state.update_data(water_goal=norm_water)
    await state.update_data(calorie_goal=norm_calories)
    # Очищаем состояние юзера, иначе, когда будем логировать воду/еду/тренировки мы вечно будем проваливаться сюда
    # Метод state.set_data({}) позволяет очистить данные. Если хотим очистить и данные, и состояние используем state.clear()
    await state.set_state(state=None)
