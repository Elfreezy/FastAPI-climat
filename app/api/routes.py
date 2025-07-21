import json
from typing import Annotated, List
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates      # jinja2
from pydantic.error_wrappers import ValidationError

from .models import UserIn, MainRequestForm, CityIn, CityInForm
from .login import authenticate_user, create_jwt_token, get_current_user
from . import db_manager
from .OpenMeteo import OpenMeteo
from .OpenMeteoParams import CurrentParams, HourlyParams, ParamsDescRu
from .Exceptions import CustomError

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
    form_data = MainRequestForm(request)
    await form_data.load_data()

    if form_data.is_valid():
        # response = await req_get_current_values(form_data.latitude, form_data.longitude)
        open_meteo = OpenMeteo()
        response = await open_meteo.forecast(latitude=form_data.latitude, longitude=form_data.longitude, current_weather=True)

        context["latitude"] = form_data.latitude
        context["longitude"] = form_data.longitude
        if response is not None:
            if response.get("errors") is None:
                context["details"] = response
            else:
                context["errors"] = response.get("errors")
    else:
        context["errors"] = form_data.errors

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
    context = {}
    form = CityInForm(request)
    await form.load_data()

    if form.is_valid():
        token = request.cookies.get('access_token')
        user = None

        if token:
            user = await get_current_user(request.cookies.get('access_token'))
        if user:
            city = CityIn(city_name=form.city_name, latitude=form.latitude, longitude=form.longitude)
            # city.weather_code = await get_weather_code(latitude=city.latitude, longitude=city.longitude)
            open_meteo = OpenMeteo()
            response = await open_meteo.forecast(latitude=city.latitude, longitude=city.longitude, current=[CurrentParams.WEATHERCODE])
            
            if response.get("current") is not None and response.get("current").get("weathercode") is not None:
                city.weather_code = response.get("current").get("weathercode")

            await db_manager.create_city(city, user.id)
            return RedirectResponse('/all_city', status_code=status.HTTP_303_SEE_OTHER)
        else:
            context["errors"] = [CustomError.NeedLogin]
    else:
        context["errors"] = form.errors
        context["city_name"] = form.city_name
        context["latitude"] = form.latitude
        context["longitude"] = form.longitude

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
        all_city = await db_manager.get_all_city_by_user_id(user_id=user.id)
    else:
        all_city = await db_manager.get_all_city()

    if all_city:
        context["items"] = all_city

    return templates.TemplateResponse(
        request=request, name="all_cities.html", context=context
    )


@router.get("/delete_city/{id}")
async def delete_city(request: Request, id: int):
    await db_manager.delete_city(id)

    return RedirectResponse('/all_city', status_code=status.HTTP_303_SEE_OTHER)


@router.get("/get_params", response_class=HTMLResponse)
async def get_city_params(request: Request):
    context = {}
    context["params"] = [param.value for param in HourlyParams]

    # Добавление описания параметров
    params_desc = {}
    for param in context["params"]:
        params_desc[param] = getattr(ParamsDescRu, param.upper()).value

    context["params_desc"] = params_desc

    return templates.TemplateResponse(
        request=request, name="find_current_params.html", context=context
    )


@router.post("/get_params", response_class=HTMLResponse)
async def get_city_params(request: Request, city_name: str = Form(), req_time: int = Form(), params: List[str] | None = Form(default=None)):
    context = {"req_time": req_time}
    query_params = {"city_name": city_name}
    token = request.cookies.get('access_token')

    if token:
        user = await get_current_user(token)
        query_params["user_id"] = user.id

    city = await db_manager.get_city_by_name(**query_params)
    if city is not None:
        open_meteo = OpenMeteo()

        # Если пользователь не выбирает параметры, передаются все возможные
        if params is None:
            params = [param for param in HourlyParams]

        response = await open_meteo.forecast(latitude=city.latitude, longitude=city.longitude, hourly=params)
        context["city_name"] = city.city_name

        if response:
            context["details"] = response
    else:
        context["errors"] = [CustomError.CityNotFound]

    context["params"] = [param.value for param in HourlyParams]

    # Добавление описания параметров
    params_desc = {}

    for param in context["params"]:
        params_desc[param] = getattr(ParamsDescRu, param.upper()).value

    # Добавление описания для вернувшихся параметров
    if context.get("details") and context.get("details").get("hourly_units"):
        for param in context.get("details").get("hourly_units"):
            params_desc[param] = getattr(ParamsDescRu, param.upper()).value

    context["params_desc"] = params_desc

    return templates.TemplateResponse(
        request=request, name="find_current_params.html", context=context
    )


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(request=request, name="auth/register.html")


@router.post("/register")
async def register(request: Request, username: str = Form(), password: str = Form()):
    errors = []
    if await db_manager.get_user_by_name(username):
        errors.append(f"Пользователь {username} уже существует")
    else:
        try:
            user = UserIn(username=username, password=password)
            await db_manager.create_user(payload=user)
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
    users = await db_manager.get_all_user()
    return templates.TemplateResponse(request=request, name="all_user.html", context={"users": users})