import warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LinearRegression

import requests
import aiohttp
import asyncio

# В первой лекции по временным рядам на 1:05:15 препод рассказывает про resample во временных рядах
async def hard_function(df, city):
    """
    Необходимо создать "тяжелую функцию". В этой функции для одного города:
    1.1. Считаются скользящим окном среднее и std. Тут же ищутся все аномалии относительно скользящих средних и std. 
         Больше эти данные полученные скользящим окном мы нигде не используем.
    1.2. Далее мы делаем groupby по сезону и считаем mean std для исходной температуры. Таким образом мы получаем профиль сезона.
    1.3. Ищем тренд (регрессия или что получше). Если обучаете регрессию, смотрите на коэффициент и возвращаете положительный или отрицательный тренд.
    1.4. Считаем среднюю, min, max температуры за все время.

    Необходимо вернуть следующую информацию:
    Город,
    Average/min/max температуры, 
    профиль сезона, 
    а также уклон тренда и список аномальных точек для города.

    Далее необходимо распараллелить эту функцию.
    """
    # Берем только данные по заданному городу
    df = df[df['city'] == city].reset_index(drop=True).copy()
    # Рассчитываем mean/std скользящим окном размера 30
    df['mean_rolling30'] = df['temperature'].rolling(30).mean()#.reset_index(0, drop=True)
    df['std_rolling30'] = df['temperature'].rolling(30).std()#.reset_index(0, drop=True)
    # Заполняем NaN'ы из первого окна первым рассчитанным значением std/mean
    df['mean_rolling30'] = df['mean_rolling30'].bfill()
    df['std_rolling30'] = df['std_rolling30'].bfill()
    # Рассчитваем границы выбросов mean(+-)2std
    df['mean-2std'] = df['mean_rolling30'] - 2 * df['std_rolling30']
    df['mean+2std'] = df['mean_rolling30'] + 2 * df['std_rolling30']
    # Проставляем флаг is_outlier_sma. True - если наблюдение выходит за границы выбросов, рассчитанных по скользящему среднему
    df.loc[(df['temperature'] < df['mean-2std']) | (df['temperature'] > df['mean+2std']), 'is_outlier_sma'] = True
    df['is_outlier_sma'] = df['is_outlier_sma'].fillna(False)
    # Считаем профиль сезона и границы выбросов для сезонов
    df_season_profile = df.groupby('season')['temperature'].agg(average_season='mean', std_season='std').reset_index(0)
    df_season_profile['mean-2std_season'] = df_season_profile['average_season'] - 2 * df_season_profile['std_season']
    df_season_profile['mean+2std_season'] = df_season_profile['average_season'] + 2 * df_season_profile['std_season']
    df = df.merge(df_season_profile, how='left', on='season')
    # Выявление выбросов на основании сезонного профиля
    df.loc[(df['temperature'] < df['mean-2std_season']) | (df['temperature'] > df['mean+2std_season']), 'is_outlier_season'] = True
    df['is_outlier_season'] = df['is_outlier_season'].fillna(False)
    # Ищем уклон тренда на основании линейной регрессии (часть информации позаимствовал отсюда https://medium.com/vortechsa/detecting-trends-in-time-series-data-using-python-2752be7d1172)
    # Для поиска тренда удалим часть наблюдений, являющихся выбросами, посчитанными через сезонный профиль
    X = df[~df['is_outlier_season']].reset_index(drop=True).index.values.reshape(-1, 1)
    y = df[~df['is_outlier_season']]['temperature'].reset_index(drop=True).values.reshape(-1, 1)
    lr_model = LinearRegression().fit(X, y)
    #y_pred = lr_model.predict(X)
    # Наклон прямой тренда. Если >0, то тренд положительный. Если <0, то тренд отрицательный
    slope = lr_model.coef_[0][0]
    # Считаем avg/min/max температур за все время
    temp_mean_alltime, temp_min_alltime, temp_max_alltime = df['temperature'].mean(), df['temperature'].min(), df['temperature'].max()

    return {
        'city': city,
        'temp_mean': temp_mean_alltime,
        'temp_min': temp_min_alltime,
        'temp_max': temp_max_alltime,
        'season_profile': df_season_profile,
        'trend_slope': slope,
        'list_outliers': df[df['is_outlier_season']]['timestamp'].to_list(),
        'raw_data': df[['city', 'timestamp', 'temperature', 'season', 'is_outlier_season']]
    }
    


async def get_post(api_key, city_name):
    # units={'metric'} позволяет указать шкалу Цельсия для вывода температуры
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units={'metric'}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status
    

async def get_info_outliers(api_key, city_name, data, season='winter'):
    # Получаем информацию по API
    response, status_code = await get_post(api_key=api_key, city_name=city_name)
    if status_code != 200:
        return 'TotalExtraError', -1, -1 
    temp_curr = response['main']['temp']
    # Выгружаем информацию по границам выбросов для данного города и сезона
    df_data = (await hard_function(data, city_name))
    low_bound = df_data['season_profile'].loc[(df_data['season_profile']['season']==season), 'mean-2std_season'].values[0]
    high_bound = df_data['season_profile'].loc[(df_data['season_profile']['season']==season), 'mean+2std_season'].values[0]

    if (temp_curr < low_bound) or (temp_curr > high_bound):
        return 1, temp_curr, df_data
    else:
        return 0, temp_curr, df_data