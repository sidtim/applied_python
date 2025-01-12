from aiogram import Router, F
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from filters import UserFoodWeightFilter
from states.state_user import ProfileUser, LoggingFood
from utils import post_nutrition_info


router = Router()

# Логирование еды
# В случае отсутствия состояния (StateFilter(None)), команда /set_profile начнет работу с этого обработчика
@router.message(StateFilter(None),
                Command("log_food"))
async def choose_product(message: Message, 
                         command: CommandObject,
                         state: FSMContext):
    # Если не переданы никакие аргументы, то command.args будет None
    if command.args is None:
        await message.answer("Ошибка: не передан аргумент. \nПередайте в качестве аргумента название продукта на <b>английском языке</b> в следующем формате: \n/log_food <i>product</i>")
        return
    try:
        input_food = command.args
        data_food, _status = await post_nutrition_info(input_food)
        await message.answer(f"{input_food.title()} — {data_food['foods'][0]['nf_calories']} ккал на {data_food['foods'][0]['serving_weight_grams']} г. Сколько грамм вы съели?")
        # Заносим данные состояний в словарь
        await state.update_data(food_name=input_food)
        await state.update_data(food_calories=float(data_food['foods'][0]['nf_calories']))
        await state.update_data(food_serving_weight_grams=float(data_food['foods'][0]['serving_weight_grams']))
        # Меняем состояние
        await state.set_state(LoggingFood.food_eat_weight)
    except:
        await message.answer("Ошибка. Данного продукта не существует или продукт введен неверно. \nВведите название продукта на <b>английском языке</b> в следующем формате: \n/log_food <i>product</i>")
        

@router.message(LoggingFood.food_eat_weight,
                UserFoodWeightFilter())
async def choose_food_eat_weight(message: Message, 
                                 state: FSMContext):
    # Сохранение данных состояния пользователя в переменную при помощи state.update_data
    await state.update_data(food_eat_weight=float(message.text))
    
    data = await state.get_data()
    # Производим расчет уоптребленных пользователем калорий
    logged_calories = (data['food_calories'] / data['food_serving_weight_grams']) * data['food_eat_weight']
    # В блоке if-else осуществляется динамическое логирование.
    # Если поле logged_calories раньше не было заполнено, то оно иницаилизируется рассчитанным logged_calories (в блоке if).
    # Если в поле logged_calories уже есть значение, то добавляем к этому значению расчеты по новому продукту (в блоке else).
    if not (await state.get_data()).get('logged_calories', None):
        await state.update_data(logged_calories=float(logged_calories))
    else:
        _cur_state = (await state.get_data())['logged_calories']
        await state.update_data(logged_calories=_cur_state + float(logged_calories))
    await message.answer(f"{await state.get_data()}")
    await message.answer(f"Записано: {logged_calories} ккал.")
    # Обнуляем состояние
    await state.set_state(state=None)
    

# Логирование воды
@router.message(Command("log_water"))
async def choose_water_drink(message: Message, 
                             command: CommandObject,
                             state: FSMContext):
    # Если не переданы никакие аргументы, то command.args будет None
    if command.args is None:
        await message.answer("Ошибка: не передан аргумент. \nПередайте в качестве аргумента количество выпитой воды в следующем формате: \n/log_water <i>numeric</i>")
        return
    try:
        input_water = command.args
        # Динамическое логировение по аналогии с предыдущим хэндлером choose_food_eat_weight
        if not (await state.get_data()).get('logged_water', None):
            await state.update_data(logged_water=float(input_water))
        else:
            _cur_state = (await state.get_data())['logged_water']
            await state.update_data(logged_water=_cur_state + float(input_water))
        await message.answer(f"{await state.get_data()}")
    except:
        await message.answer("Ошибка: некорректно введен аргумент. \nПередайте в качестве аргумента количество выпитой воды в следующем формате: \n/log_water <i>numeric</i>")


# Логирование тренировок
@router.message(Command("log_workout"))
async def choose_workout_info(message: Message, 
                              command: CommandObject,
                              state: FSMContext):
    # Если не переданы никакие аргументы, то command.args будет None
    if command.args is None:
        await message.answer("Ошибка: не передан аргумент. \nПередайте аргументы с информацией о типе тренировки (workout_type) и времени тренировки в минутах (workout_time) в следующем формате: \n/log_workout <i>workout_type</i> <i>workout_time</i>")
        return
    try:
        workout_type, workout_time = command.args.split(" ", maxsplit=1)
        workout_time = float(workout_time)
        # Если беговая тренировка, то сжигается 100 ккал. за каждые 10 минут бега.
        # Любая другая тренировка сжигает 50 ккал. за каждые 10 минут активности.
        burned_calories = 100 * workout_time // 10 if workout_type.lower() == 'бег' else 50 * workout_time // 10
        # Дополнительно выпивает 150 мл. воды за каждые 10 минут бега.
        # При любой другой активности дополнительно выпиваем 100 мл. за каждые 10 минут активности.
        _drinked_water = 150 * workout_time // 10 if workout_type.lower() == 'бег' else 100 * workout_time // 10

        if not (await state.get_data()).get('burned_calories', None):
            await state.update_data(burned_calories=float(burned_calories))
        else:
            _cur_state = (await state.get_data())['burned_calories']
            await state.update_data(burned_calories=_cur_state + float(burned_calories))

        # Добавляем к норме воды в сутки объем воды, который необходимо восполнить после тренировки.
        if not (await state.get_data()).get('water_goal', None):
            await message.answer("У вас отсутствует рассчитанная норма воды в сутки. \nЗаполните, пожалуйста, свой профиль, введя команду <b>/set_profile</b>")
        else:
            _cur_state = (await state.get_data())['water_goal']
            await state.update_data(water_goal=_cur_state + float(_drinked_water))
        await message.answer(f"{await state.get_data()}")
        await message.answer(f"{workout_type.lower().title()} {workout_time} минут — {burned_calories} ккал. Дополнительно: выпейте {_drinked_water} мл воды.")

    except:
        await message.answer("Ошибка. \nПередайте аргументы с информацией о типе тренировки (workout_type) и времени тренировки в минутах (workout_time) в следующем формате: \n/log_workout <i>workout_type</i> <i>workout_time</i>")


# Прогресс по воде и калориям
@router.message(Command("check_progress"))
async def choose_progress_bar(message: Message, 
                              command: CommandObject,
                              state: FSMContext):
    data = await state.get_data()

    if not (data.get("water_goal", None) and data.get("calorie_goal", None)):
        await message.answer("Отсутствуют сведения по ежедневным нормам воды и калорий. \nЗаполните, пожалуйста свой профиль, введя команду <b>/set_profile</b>")
        return
    if not data.get("logged_water", None):
        data['logged_water'] = 0
    if not data.get("logged_calories", None):
        data['logged_calories'] = 0
    if not data.get("burned_calories", None):
        data['burned_calories'] = 0

    await message.answer(
        f"""
        Прогресс:
        Вода:
        - Выпито: {data["logged_water"]} мл. из {data["water_goal"]}
        - Осталось: {data["water_goal"] - data["logged_water"]} мл.
        
        Калории:
        - Потреблено: {data["logged_calories"]} ккал. из {data["calorie_goal"]}
        - Сожжено: {data["burned_calories"]} ккал.
        - Баланс: {data["logged_calories"] - data["burned_calories"]} ккал."""
    )
    