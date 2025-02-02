from pydantic import BaseModel
from fastapi import Request
from typing import Optional, Annotated


class Calculater(BaseModel):
    num1: int
    num2: int


class User(BaseModel):
    id: int
    age: int
    name: str


class Feedback(BaseModel):
    name: str
    message: str


class Task1Form(BaseModel):
    latitude: float
    longitude: float


class CityIn(BaseModel):
    city_name: str
    latitude: float
    longitude: float
    weather_code: Optional[int] = None


class CityInForm:

    def __init__(self, request: Request):
        self.request: Request = request
        self.city_name: Optional[str]
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None

    async def load_data(self):
        form = await self.request.form()
        self.city_name = form.get("city_name")
        self.latitude = form.get("latitude")
        self.longitude = form.get("longitude")
