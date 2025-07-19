import httpx
import asyncio

from .OpenMeteoParams import Params, ParamsDescRu


class OpenMeteo():
    request_timeout: float = 10.0

    async def forecast(
        self,
        latitude: float,
        longitude: float, 
        forecast_days: int = 1,
        current_weather: bool = False, # Получить значения параметров на текущий момент
        daily: list = None
        ):
        url = 'http://api.open-meteo.com/v1/forecast'

        params = {
        'latitude': latitude,
        'longitude': longitude, 
        'forecast_days': forecast_days,
        'current_weather': 'true' if current_weather else 'false',
        }

        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(url, params=params)
                response = response.json()

                if response.get('current_weather') is not None:
                    response["value_description_ru"] = {}
                    for key, value in response.get('current_weather').items():
                        if hasattr(ParamsDescRu, key.upper()):
                            response["value_description_ru"][key] = getattr(ParamsDescRu, key.upper())
                        else:
                            response["value_description_ru"][key] = value

                return response
        except Exception as e:
            print(e)
            return {"errors": ["Превышено время ожидания сервиса"]}