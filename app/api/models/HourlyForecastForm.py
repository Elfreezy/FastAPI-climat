from .MainRequestForm import MainRequestForm
from .OpenMeteo import OpenMeteo
from .OpenMeteoParams import HourlyParams, ParamsDescRu


class HourlyForecastForm(MainRequestForm):

    def __init__(self, city_name:str = None, hour:int = None):
        super().__init__()
        self.city_name  = city_name
        self.hour       = hour
    
    async def get_forecast(self, params: list[HourlyParams] = None):
        open_meteo = OpenMeteo()

        if not params:
            params = await self.get_list_hourly_params()

        if self.hour:
            response = await open_meteo.forecast(latitude=self.latitude, longitude=self.longitude, hourly=params)
            
            if response.get("errors") is not None:
                self.errors += response.get("errors")
            else:                
                for hourly_unit in response.get("hourly_units"):
                    response["hourly"][hourly_unit] = response["hourly"][hourly_unit][self.hour]
            return response
        
        return None
    
    '''
    Возвращается: list[<имя параметра>]
    '''
    async def get_list_hourly_params(self):
        return [param.name.lower() for param in HourlyParams]
    
    '''
    Передается: list[<имя параметра>]
    Возвращает: dict{<имя параметра>: <описание на русском>}
    '''
    async def get_dict_params_desc(self, list_params):
        # Добавление описания параметров
        params_desc = {}
        for param in list_params:
            params_desc[param] = getattr(ParamsDescRu, param.upper()).value
        return params_desc
            
