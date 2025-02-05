import json
from typing import Annotated, List
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates      # jinja2
from pydantic.error_wrappers import ValidationError

from .models import UserIn, MainRequestForm, CityIn, CityInForm
from .service import req_get_current_values, get_weather_code
from .login import authenticate_user, create_jwt_token, get_current_user
from . import db_manager


router = APIRouter()
templates = Jinja2Templates(directory="api/templates")


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
        response = await req_get_current_values(form_data.latitude, form_data.longitude)

        context["latitude"] = form_data.latitude
        context["longitude"] = form_data.longitude
        if response is not None:
            context["details"] = response
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
        city = CityIn(city_name=form.city_name, latitude=form.latitude, longitude=form.longitude)
        city.weather_code = await get_weather_code(latitude=city.latitude, longitude=city.longitude)

        token = request.cookies.get('access_token')
        user = None

        if token:
            user = await get_current_user(request.cookies.get('access_token'))

        await db_manager.create_city(city, user.id)

        return RedirectResponse('/all_city', status_code=status.HTTP_303_SEE_OTHER)
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
        all_city = await db_manager.get_all_city_by_id(user_id=user.id)
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
    params = ['temperature_2m', 'pressure_msl', 'surface_pressure', 'wind_speed_10m', 'weather_code']
    context = {"params": params}

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
        response = await req_get_current_values(city.latitude, city.longitude, params, hourly=True)
        context["city_name"] = city.city_name
        context["details"] = response

    params = ['temperature_2m', 'pressure_msl', 'surface_pressure', 'wind_speed_10m', 'weather_code']
    context["params"] = params

    return templates.TemplateResponse(
        request=request, name="find_current_params.html", context=context
    )


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(request=request, name="auth/register.html")


@router.post("/register")
async def register(request: Request, username: str = Form(), password: str = Form()):
    errors = []
    if db_manager.get_user_by_name(username):
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