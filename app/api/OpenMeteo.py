import httpx
import asyncio

from .OpenMeteoParams import CurrentParams, HourlyParams, ParamsDescRu


class OpenMeteo():
    request_timeout: float = 10.0

    async def request(self, url, params):
        data = None
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(url, params=params)
                data = response.json()

                await self.get_params_description(data)
        except Exception as e:
            print(e)
            data = {"errors": ["Превышено время ожидания сервиса"]}
        
        return data

    async def forecast(
        self,
        latitude: float,
        longitude: float, 
        forecast_days: int = 1,
        current_weather: bool = False, # Получить значения параметров на текущий момент
        current: list[CurrentParams] | None = None,
        hourly: list[HourlyParams] | None = None,
        daily: list | None = None,
        ):
        url = 'http://api.open-meteo.com/v1/forecast'

        params = {
        'latitude': latitude,
        'longitude': longitude, 
        'forecast_days': forecast_days,
        'current_weather': 'true' if current_weather else 'false',
        'current': ','.join(current) if current is not None else [],
        'hourly': ','.join(hourly) if hourly is not None else [],
        'daily': ','.join(daily) if daily is not None else [],
        }
        
        data = await self.request(url, params)
        return data
        
    async def get_params_description(self, response_json):
        if response_json.get('current_weather') is not None:
            response_json["value_description_ru"] = {}
            for key, value in response_json.get('current_weather').items():
                if hasattr(ParamsDescRu, key.upper()):
                    response_json["value_description_ru"][key] = getattr(ParamsDescRu, key.upper())
                else:
                    response_json["value_description_ru"][key] = value