from pydantic import BaseModel
from fastapi import Request
from typing import Optional, Annotated, List


class User(BaseModel):
    id: int
    age: int
    name: str


class MainRequestForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.latitude: Optional[str] = None
        self.longitude: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.latitude = form.get("latitude")
        self.longitude = form.get("longitude")

    def is_valid(self):
        if not self.latitude is None:
            try:
                if not (float(self.latitude) >= -90.0 and float(self.latitude) <= 90):
                    self.errors.append("Широта определена в диапазоне [-90.0, 90.0]")
            except ValueError:
                self.errors.append("Широта: некорректный формат данных")

        if not self.longitude is None:
            try:
                if not (float(self.longitude) >= -180.0 and float(self.longitude) <= 180):
                    self.errors.append("Долгота определена в диапазоне [-180.0, 180.0]")
            except ValueError:
                self.errors.append("Долгота: некорректный формат данных")

        if not self.errors:
            return True

        return False


class CityIn(BaseModel):
    city_name: str
    latitude: float
    longitude: float
    weather_code: Optional[int] = None


class CityInForm(MainRequestForm):

    def __init__(self, request: Request):
        super().__init__(request)
        self.city_name: Optional[str]

    async def load_data(self):
        form = await self.request.form()
        self.city_name = form.get("city_name")
        self.latitude = form.get("latitude")
        self.longitude = form.get("longitude")
