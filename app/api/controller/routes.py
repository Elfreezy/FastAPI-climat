'''
В контроллере должна происходить только распаковка данных, передача их в модель, вызов методов модели и отправка обработанных данных во View
'''

import json
from typing import Annotated, List
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates      # jinja2
from pydantic.error_wrappers import ValidationError

from ..utils.login import authenticate_user, create_jwt_token, get_current_user
from ..models.OpenMeteoParams import CurrentParams, HourlyParams, ParamsDescRu # Убрать от сюда
from ..models.Exceptions import CustomError
from ..models.DataBaseManager import DataBaseManager
from ..models.CurrentForecastForm import CurrentForecastForm
from ..models.HourlyForecastForm import HourlyForecastForm
from ..models.CityForm import CityForm
from ..models.UserIn import UserIn
from ..models.CityIn import CityIn

router = APIRouter()
templates = Jinja2Templates(directory="app/api/templates")


@router.get('/')
def read_root(request: Request):
    return templates.TemplateResponse(
       request=request, name="base.html"
    )

@router.post('/get_current_values')
async def get_current_values(request: Request):
    context = {}
    form_data = await request.form()
    current_forcast = CurrentForecastForm()

    if await current_forcast.load_data(latitude=form_data.get("latitude"), longitude=form_data.get("longitude")):
        response = await current_forcast.get_forecast()

        if response:
            context["details"] = response

    if current_forcast.errors:
        context["errors"] = current_forcast.errors

    # Заполнение отправленными значениями
    for key, value in form_data.items():
        context[key] = value

    return templates.TemplateResponse(
        request=request, name="current_values.html", context=context
    )

@router.get('/get_current_values')
async def read_current_values(request: Request):
    template = templates.TemplateResponse(
        request=request, name="current_values.html"
    )

    return template

@router.get("/city/add", response_class=HTMLResponse)
async def create_city(request: Request):
    return templates.TemplateResponse(
        request=request, name="add_city.html"
    )


@router.post("/city/add", response_class=HTMLResponse)
async def create_city(request: Request):
    context = {"errors": []}
    form_data = await request.form()

    if form_data:
        city_form = CityForm(city_name=form_data.get("city_name"))

        if await city_form.load_data(latitude=form_data.get("latitude"), longitude=form_data.get("longitude")):
            token = request.cookies.get('access_token')
            user = None
            response = await city_form.get_forecast(params=[CurrentParams.WEATHERCODE])

            if token:
                user = await get_current_user(request.cookies.get('access_token'))
            
            if user:
                city = CityIn(city_name=city_form.city_name, latitude=city_form.latitude, longitude=city_form.longitude)

                if response.get("current") is not None and response.get("current").get("weathercode") is not None:
                    city.weather_code = response.get("current").get("weathercode")
                
                await DataBaseManager.create_city(city, user.id)
                return RedirectResponse('/all_city', status_code=status.HTTP_303_SEE_OTHER)
            else:
                context["errors"] += [CustomError.NeedLogin]
    
        if city_form.errors:
            context["errors"] += city_form.errors

    # Заполнение отправленными значениями
    for key, value in form_data.items():
        context[key] = value
    
    return templates.TemplateResponse(
        request=request, name="add_city.html", context=context
    )


@router.get("/all_city", response_class=HTMLResponse)
async def read_all_city(request: Request):
    token = request.cookies.get('access_token')
    user = None
    context = {}

    if token:
        user = await get_current_user(token)

    if user:
        all_city = await DataBaseManager.get_all_city_by_user_id(user_id=user.id)
    else:
        all_city = await DataBaseManager.get_all_city()

    if all_city:
        context["items"] = all_city

    return templates.TemplateResponse(
        request=request, name="all_cities.html", context=context
    )


@router.get("/delete_city/{id}")
async def delete_city(request: Request, id: int):
    await DataBaseManager.delete_city_by_id(id)
    return RedirectResponse('/all_city', status_code=status.HTTP_303_SEE_OTHER)


@router.get("/get_params", response_class=HTMLResponse)
async def get_city_params(request: Request):
    context = {}
    hourly_forecast_form    = HourlyForecastForm()
    context["params"]       = await hourly_forecast_form.get_list_hourly_params()
    context["params_desc"]  = await hourly_forecast_form.get_dict_params_desc(context["params"])

    return templates.TemplateResponse(
        request=request, name="find_current_params.html", context=context
    )


@router.post("/get_params", response_class=HTMLResponse)
async def get_city_params(request: Request, params: List[str] | None = Form(default=None)):
    context = {"errors": []}
    hourly_forecast_form = HourlyForecastForm()
    form_data = await request.form()
    token = request.cookies.get('access_token')

    if form_data:
        if token:
            user = await get_current_user(token)

            if user:
                city = await DataBaseManager.get_city_by_name(city_name=form_data.get("city_name"), user_id=user.id)

                if city:
                    hourly_forecast_form.city_name  = city.city_name
                    hourly_forecast_form.hour       = int(form_data.get("req_time"))

                    if await hourly_forecast_form.load_data(latitude=city.latitude, longitude=city.longitude):
                        response = await hourly_forecast_form.get_forecast(params=params)
                        
                        if response:
                            context["details"] = response
                    
                    context["errors"] += hourly_forecast_form.errors

    # Заполнение отправленными значениями
    for key, value in form_data.items():
        context[key] = value
    
    context["params"]       = await hourly_forecast_form.get_list_hourly_params()
    list_params             = context["params"].copy()

    if context.get("details") is not None and context.get("details").get("hourly_units"):
        list_params += [x for x in context["details"]["hourly_units"]]

    context["params_desc"]  = await hourly_forecast_form.get_dict_params_desc(list_params)

    return templates.TemplateResponse(
        request=request, name="find_current_params.html", context=context
    )


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(request=request, name="auth/register.html")


@router.post("/register")
async def register(request: Request, username: str = Form(), password: str = Form()):
    errors = []
    if await DataBaseManager.get_user_by_name(username):
        errors.append(f"Пользователь {username} уже существует")
    else:
        try:
            user = UserIn(username=username, password=password)
            await DataBaseManager.create_user(payload=user)
            return RedirectResponse("/?alert=Successfully%20Registered", status_code=status.HTTP_302_FOUND)
        except ValidationError as e:
            errors_list = json.loads(e.json())
            for item in errors_list:
                errors.append(item.get("loc")[0] + ": " + item.get("msg"))

    return templates.TemplateResponse(request=request, name="auth/register.html", context={"errors": errors})


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="auth/login.html")


@router.post("/login")
async def login(request: Request, username: str = Form(), password: str = Form()):
    errors = []
    user = await authenticate_user(username=username, password=password)
    if not user:
        errors.append("Некорректный логин или пароль")
        return templates.TemplateResponse(request=request, name="auth/login.html", context={"errors": errors})
    access_token = await create_jwt_token(data={"sub": username})
    response = RedirectResponse(
        "/?alert=Successfully Logged In", status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key="access_token", value=access_token, httponly=True
    )
    return response


@router.get("/all_user")
async def all_user(request: Request):
    users = await DataBaseManager.get_all_user()
    return templates.TemplateResponse(request=request, name="all_user.html", context={"users": users})