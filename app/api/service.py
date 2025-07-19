import httpx
import ssl
import asyncio

from . import db_manager
from .models import CityIn
from .OpenMeteo import OpenMeteo
from .OpenMeteoParams import CurrentParams

URL = 'http://api.open-meteo.com/v1/forecast'
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
        open_meteo = OpenMeteo()
        response = await open_meteo.forecast(latitude=line.latitude, longitude=line.longitude, current=[CurrentParams.WEATHERCODE])

        if response is not None and response.get("current") is not None and response.get("current").get("weathercode") is not None:
            new_weather_code = response.get("current").get("weathercode")

            if new_weather_code != line.weather_code:
                await db_manager.update_city(line.id, {'weather_code': new_weather_code})