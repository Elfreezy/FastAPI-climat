from .MainRequestForm import MainRequestForm
from .OpenMeteo import OpenMeteo


class CurrentForecastForm(MainRequestForm):

    def __init__(self):
        super().__init__()
    
    async def get_forecast(self):
        open_meteo = OpenMeteo()
        response = await open_meteo.forecast(latitude=self.latitude, longitude=self.longitude, current_weather=True)

        if response.get("errors") is not None:
            self.errors += response.get("errors")
            return None 
        
        return response
        
