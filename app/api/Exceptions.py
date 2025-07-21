from enum import StrEnum

class CustomError(StrEnum):
    UserNotFound = "Пользователь не найден"
    NeedLogin = "Необходимо авторизоваться"
    CityNotFound = "Город не найден"