from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from werkzeug.security import generate_password_hash

from .db import city, database, engine, user
from .models import CityIn, UserIn


async def create_user(payload: UserIn):
    query = user.insert().values(username=payload.username,
                                 password_hash=generate_password_hash(payload.password))
    return await database.execute(query=query)


async def get_all_user():
    query = user.select()
    return await database.fetch_all(query=query)


async def get_user_by_name(username: str):
    query = user.select().where(user.c.username==username)
    return await database.fetch_one(query=query)


async def create_city(payload: CityIn, user_id: int = None):
    dict_query = payload.dict()
    if user_id:
        dict_query["user_id"] = user_id
    query = city.insert().values(**dict_query)

    return await database.execute(query=query)


async def read_city(id: int):
    query = city.select(city.c.id==id)
    return await database.fetch_one(query=query)


async def update_city(id: int, payload: dict):
    query = city.update().where(city.c.id == id).values(**payload)
    return await database.execute(query=query)


async def delete_city(id: int):
    query = city.delete().where(city.c.id==id)

    return await database.execute(query=query)


async def get_all_city():
    query = city.select()
    return await database.fetch_all(query=query)


async def get_all_city_by_user_id(user_id: int):
    query = city.select().where(city.c.user_id==user_id)
    return await database.fetch_all(query=query)


async def get_city_by_name(city_name: str, user_id: int = None):
    query = city.select().where(city.c.city_name == city_name)

    if user_id:
        query = query.where(city.c.user_id==user_id)

    return await database.fetch_one(query=query)