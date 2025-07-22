from pydantic import BaseModel

'''
Класс для проверки типов данных и записи экзепляра класса в БД
'''
class UserIn(BaseModel):
    username: str
    password: str
