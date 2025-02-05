import httpx
import ssl
import asyncio

from . import db_manager
from .models import CityIn

URL = 'https://api.open-meteo.com/v1/forecast'
# ctx = ssl.create_default_context()
# ctx.load_cert_chain(certfile="path/to/client.pem")


async def req_get_current_values(latitude, longitude, req_values=None, hourly=False):
    if req_values is None or len(req_values) == 0:
        req_values = ['temperature_2m',
                      'pressure_msl',
                      'surface_pressure',
                      'wind_speed_10m',
                      'weather_code']

    type_params = "hourly" if hourly == True else "current"

    params = {"latitude": latitude,
              "longitude": longitude,
              "forecast_days": 1,
              type_params: req_values}

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(URL, params=params)

        return response.json()


async def get_weather_code(latitude, longitude):
    response = await req_get_current_values(latitude, longitude)

    if response.get("current") is not None:
        return response.get("current").get("weather_code")

    return None


async def update_weather_codes() -> None:
    cities = await db_manager.get_all_city()

    for line in cities:
        city = CityIn(city_name=line.city_name,
                      latitude=line.latitude,
                      longitude=line.longitude,
                      weather_code=line.weather_code)

        city.weather_code = await get_weather_code(city.latitude, city.longitude)

        await db_manager.update_city(line.id, city)