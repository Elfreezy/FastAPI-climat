from . import db_manager
from .models import CityIn
from .OpenMeteo import OpenMeteo
from .OpenMeteoParams import CurrentParams

# Обновление параметра - Погодный код
async def update_weather_codes() -> None:
    cities = await db_manager.get_all_city()

    for line in cities:
        open_meteo = OpenMeteo()
        response = await open_meteo.forecast(latitude=line.latitude, longitude=line.longitude, current=[CurrentParams.WEATHERCODE])

        if response is not None and response.get("current") is not None and response.get("current").get("weathercode") is not None:
            new_weather_code = response.get("current").get("weathercode")

            if new_weather_code != line.weather_code:
                await db_manager.update_city(line.id, {'weather_code': new_weather_code})