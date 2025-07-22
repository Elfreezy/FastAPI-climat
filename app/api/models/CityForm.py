from .MainRequestForm import MainRequestForm
from .OpenMeteoParams import CurrentParams
from .OpenMeteo import OpenMeteo


class CityForm(MainRequestForm):
    def __init__(self, city_name: str):
        super().__init__()
        self.city_name = city_name

    async def get_forecast(self, params: list[CurrentParams]):
        open_meteo = OpenMeteo()
        response = await open_meteo.forecast(latitude=self.latitude, longitude=self.longitude, current=params)

        if response.get("errors") is not None:
            self.errors += response.get("errors")
            return None 
        
        return response