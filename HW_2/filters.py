
from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


class UserWeightFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, str]:
        try:
            if float(message.text) >= 2 and float(message.text) <= 645:
                return True
            else:
                await message.answer(text="Incorrect weight. \nWeight must be in range [2, 645] kg.")
        except:
            await message.answer(text="Incorrect weight. \nWeight must be in range [2, 645] kg.")
        return False


class UserHeightFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, str]:
        try:
            if float(message.text) >= 60 and float(message.text) <= 272:
                return True
            else: 
                await message.answer(text="Incorrect Height. \nHeight must be in range [60, 272] cm.")
        except:
            await message.answer(text="Incorrect Height. \nHeight must be in range [60, 272] cm.")
        return False


class UserAgeFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, str]:
        try:
            if float(message.text) >= 16 and float(message.text) <= 125:
                return True
            else:
                await message.answer(text="Incorrect Age. \nAge must be in range [16, 125] years.")
        except:
            await message.answer(text="Incorrect Age. \nAge must be in range [16, 125] years.")
        return False


class UserActionTimeFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, str]:
        try:
            if float(message.text) >= 0 and float(message.text) <= 300:
                return True
            else:
                await message.answer(text="Incorrect action time. \nAction time must be in range [0, 300] minutes.")
        except:
            await message.answer(text="Incorrect action time. \nAction time must be in range [0, 300] minutes.")
        return False


class UserObjCaloriesFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, str]:
        try:
            if float(message.text) >= 1200 and float(message.text) <= 3000:
                return True
            else:
                await message.answer(text="Incorrect object of calories. \nObject of calories must be in range [1200, 3000] calories.")
        except:
            await message.answer(text="Incorrect object of calories. \nObject of calories must be in range [1200, 3000] calories.")
        return False
    

class UserFoodWeightFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, str]:
        try:
            if float(message.text) >= 0 and float(message.text) <= 2000:
                return True
            else:
                await message.answer(text="Incorrect data. It's impossible to eat such large portion. \nWeight of eaten food must be in range [0, 2000] gramm.")
        except:
            await message.answer(text="Incorrect data. \nWeight of eaten food must be in range [0, 2000] gramm.")
        return False