from werkzeug.security import generate_password_hash


from .CityIn import CityIn
from .UserIn import UserIn
from ..utils.db import city, database, user


class DataBaseManager():

    @classmethod
    async def create_user(self, payload: UserIn):
        query = user.insert().values(username=payload.username,
                                    password_hash=generate_password_hash(payload.password))
        return await database.execute(query=query)
    

    @classmethod
    async def create_city(self, payload: CityIn, user_id: int = None):
        dict_query = payload.dict()
        if user_id:
            dict_query["user_id"] = user_id
        query = city.insert().values(**dict_query)

        return await database.execute(query=query)
    

    @classmethod
    async def get_all_user(self):
        query = user.select()
        return await database.fetch_all(query=query)
    

    @classmethod
    async def get_all_city(self):
        query = city.select()
        return await database.fetch_all(query=query)
    

    @classmethod
    async def get_all_city_by_user_id(self, user_id: int):
        query = city.select().where(city.c.user_id==user_id)
        return await database.fetch_all(query=query)
    

    @classmethod
    async def get_city_by_name(self, city_name: str, user_id: int = None):
        query = city.select().where(city.c.city_name == city_name)

        if user_id:
            query = query.where(city.c.user_id==user_id)

        return await database.fetch_one(query=query)


    @classmethod
    async def get_user_by_name(self, username: str):
        query = user.select().where(user.c.username==username)
        return await database.fetch_one(query=query)
    

    @classmethod
    async def get_city_by_id(self, id: int):
        query = city.select(city.c.id==id)
        return await database.fetch_one(query=query)
    

    @classmethod
    async def update_city_by_id(self, id: int, payload: dict):
        query = city.update().where(city.c.id == id).values(**payload)
        return await database.execute(query=query)
    

    @classmethod
    async def delete_city_by_id(self, id: int):
        query = city.delete().where(city.c.id==id)

        return await database.execute(query=query)

