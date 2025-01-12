import warnings
warnings.filterwarnings('ignore')

import aiohttp
from config import WEATHER_API_SECRET, NUTRITION_API_ID, NUTRITION_API_SECRET

async def post_nutrition_info(product_name, 
                              api_id=NUTRITION_API_ID, 
                              api_secret=NUTRITION_API_SECRET):
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, 
                                headers={"x-app-id": f"{api_id}",
                                         "x-app-key": f"{api_secret}"},
                                         json={"query": f"{product_name}"}) as response:
            return await response.json(), response.status
        
async def get_weather_info(city_name, api_secret=WEATHER_API_SECRET):
    # units={'metric'} позволяет указать шкалу Цельсия для вывода температуры
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_secret}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status
        

async def calc_norm_calories(user_weight: float,
							 user_height: float,
							 user_age: float,
							 user_action_time: float):
	if user_action_time <= 15:
		return 10 * user_weight + 6.25 * user_height - 5 * user_age + 0
	elif user_action_time <= 60:
		return 10 * user_weight + 6.25 * user_height - 5 * user_age + 200
	else:
		return 10 * user_weight + 6.25 * user_height - 5 * user_age + 400


async def calc_norm_water(user_weight: float,
						  user_action_time: float,
						  user_city:str):
	curr_temperature, _status = await get_weather_info(city_name=user_city.lower().title())
	print(user_weight, user_action_time, user_city, curr_temperature['main']['temp'])
	return 30 * user_weight + 500 * (user_action_time // 30) + 500 * (curr_temperature['main']['temp'] > 25)