"""
Задание 2.
Зарегистрироваться на https://openweathermap.org/api и написать функцию,
которая получает погоду в данный момент для города,
название которого получается через input. https://openweathermap.org/current
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPEN_WEATHER_MAP_TOKEN = os.getenv("OPEN_WEATHER_MAP_TOKEN")


def kelvin_to_celsius(temperature):
    return round(temperature - 273.15, 1)


def get_city_temperature(city, country=None):
    city_and_country = city if country is None else f"{city},{country}"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_and_country}" \
          f"&APPID={OPEN_WEATHER_MAP_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        kelvin_temperature = json_data['main']['temp']
        return kelvin_to_celsius(kelvin_temperature)


# print(f"Temperature in Moscow is: {get_city_temperature('Moscow')}")
# print(f"Temperature in London,UK is: {get_city_temperature('London', 'uk')}")

city_name = input('Please enter city name >>> ')
print(f"Temperature in {city_name} is: {get_city_temperature(city_name)}")