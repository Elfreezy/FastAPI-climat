from pydantic import BaseModel
from typing import Optional, Annotated, List

'''
Класс для проверки типов данных и записи экзепляра класса в БД
'''
class CityIn(BaseModel):
    city_name: str
    latitude: float
    longitude: float
    weather_code: Optional[int] = None