import streamlit as st
import pandas as pd

import plotly.express as px
import asyncio

from utils import get_info_outliers

st.title("HW_1. Тимонин Андрей Сергевич")
st.header("Загрузка данных")

API_KEY = '1824818bd112e614de8890e506dbabfe'
list_city_name = ['New York', 'London', 'Paris', 'Tokyo', 'Moscow', 'Sydney',
				  'Berlin', 'Beijing', 'Rio de Janeiro', 'Dubai', 'Los Angeles',
				  'Singapore', 'Mumbai', 'Cairo', 'Mexico City']

uploaded_file = st.file_uploader("Выберите CSV-файл", type=['csv'])
if uploaded_file is not None:
	df = pd.read_csv(uploaded_file)
	df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%d")
	st.dataframe(df.head())

	input_city_name = st.selectbox("Выберите город в котором вы хотите узнать текущую температуру", 
				tuple(list_city_name))

	input_api = st.text_input('Введите свой API-ключ с сайта [openweathermap.org](https://openweathermap.org/)')
	if input_api == "":
		st.text("Статистика по погоде не будет отображена, пока вы не введете свой API-ключ👆👆👆")
	else:
		resp_flag, resp_curr_temp, df_data = asyncio.run(get_info_outliers(api_key=input_api, city_name=input_city_name, data=df, season='winter'))
		if resp_flag == 'TotalExtraError':
			st.text("""{"code":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}""")
		else:
			if resp_flag == 1:
				st.text(f"""Текущая температура в городе {input_city_name}: {resp_curr_temp}℃. \nДанная температура является аномальной для этого сезона.""")
			elif resp_flag == 0:
				st.text(f"""Текущая температура в городе {input_city_name}: {resp_curr_temp}℃. \nДанная температура является нормальной для этого сезона.""")

			if df_data:
				st.subheader(f"Описательные статистики по данным за 10 лет")
				st.write(df_data['raw_data'][['temperature']].describe())
				# st.text(f"Исторически минимальная температура в городе {input_city_name}: {round(df_data['temp_min'], 2)}℃")
				# st.text(f"Исторически максимальная температура в городе {input_city_name}: {round(df_data['temp_max'], 2)}℃")
				# st.text(f"Исторически средняя температура в городе {input_city_name}: {round(df_data['temp_mean'], 2)}℃")
				st.subheader(f"Временной ряд температур с выделением аномалий")
				df_data['raw_data']['is_outlier_season'] = df_data['raw_data']['is_outlier_season'].replace({True: "Аномальные значения"})
				fig1 = px.line(df_data['raw_data'], x='timestamp', y="temperature", title=f"""График температур (℃) в городе {input_city_name}""")
				fig2 = px.scatter(df_data['raw_data'].loc[df_data['raw_data']['is_outlier_season']=='Аномальные значения'], y="temperature", x="timestamp", color="is_outlier_season", color_discrete_sequence=['red'])
				st.plotly_chart(fig1.add_trace(fig2.data[0]))
				st.subheader(f"Сезонный профиль для города {input_city_name}")
				st.write(df_data['season_profile'])
else:
	st.text("Чтобы продолжить, выберите CSV-файл (можете взять файл temperature_data.csv из моего репозитория).")





