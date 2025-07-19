from enum import StrEnum

class Params(StrEnum):
    TEMPERATURE_2M      = 'temperature_2m'
    PRESSURE_MSL        = 'pressure_msl'
    SURFACE_PRESSURE    = 'surface_pressure'
    WIND_SPEED_10M      = 'wind_speed_10m'
    WEATHER_CODE        = 'weather_code'
    FORECAST_DAYS       = 'forecast_days'
    LATITUDE            = 'latitude'
    LONGITUDE           = 'longitude'


class ParamsDescRu(StrEnum):
    TEMPERATURE_2M      = 'Температура воздуха на высоте 2 метров над землей'
    PRESSURE_MSL        = 'Давление, скорректированное до уровня моря'
    SURFACE_PRESSURE    = 'Поверхностное давление'
    WIND_SPEED_10M      = 'Скорость воздуха на высоте 2 метров над землей'
    WEATHER_CODE        = 'Погодный код'
    FORECAST_DAYS       = 'Количество дней на который совершается прогноз'
    LATITUDE            = 'Широта'
    LONGITUDE           = 'Долгота'
    TIME                = 'Время'
    INTERVAL            = 'Интервал'
    TEMPERATURE         = 'Температура'
    WINDSPEED           = 'Скорость ветра'
    WINDDIRECTION       = 'Направление ветра'
    IS_DAY              = 'Сейчас день (0/1 - нет/да)'
    WEATHERCODE         = 'Погодный код'