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
        response_json = None
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(url, params=params)
                response_json = response.json()

                await self.get_params_description(response_json)
        except Exception as e:
            print(e)
            response_json["errors"] = ["Превышено время ожидания сервиса"]
        
        return response_json
        
    async def get_params_description(self, response_json):
        if response_json.get('current_weather') is not None:
            response_json["value_description_ru"] = {}
            for key, value in response_json.get('current_weather').items():
                if hasattr(ParamsDescRu, key.upper()):
                    response_json["value_description_ru"][key] = getattr(ParamsDescRu, key.upper())
                else:
                    response_json["value_description_ru"][key] = value