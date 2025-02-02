from .db import city, database
from .models import CityIn


async def create_city(payload: CityIn):
    query = city.insert().values(**payload.dict())

    return await database.execute(query=query)


async def read_city(id: int):
    query = city.select(city.c.id==id)
    return await database.fetch_one(query=query)


async def update_city(id: int, payload: CityIn):
    query = city.update().where(city.c.id == id).values(**payload.dict())
    return await database.execute(query=query)


async def delete_city(id: int):
    query = city.delete().where(city.c.id==id)

    return await database.execute(query=query)


async def get_all_city():
    query = city.select()
    return await database.fetch_all(query=query)


async def get_city_by_name(city_name: str):
    query = city.select().where(city.c.city_name==city_name)
    return await database.fetch_one(query=query)