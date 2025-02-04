from typing import Annotated, List
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates      # jinja2

from .models import User, MainRequestForm, CityIn, CityInForm
from .service import req_get_current_values, get_weather_code
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

        await db_manager.create_city(city)

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
    all_city = await db_manager.get_all_city()

    return templates.TemplateResponse(
        request=request, name="all_cities.html", context={"items": all_city}
    )


@router.get("/delete_city/{id}")
async def delete_city(request: Request, id: int):
    await db_manager.delete_city(id)

    return RedirectResponse('/all_city', status_code=status.HTTP_303_SEE_OTHER)


@router.get("/get_params", response_class=HTMLResponse)
async def get_city_params(request: Request):
    params = ['temperature_2m', 'pressure_msl', 'surface_pressure', 'wind_speed_10m', 'weather_code']
    return templates.TemplateResponse(
        request=request, name="find_current_params.html", context={"params": params}
    )


@router.post("/get_params", response_class=HTMLResponse)
async def get_city_params(request: Request, city_name: str = Form(), req_time: int = Form(), params: List[str] | None = Form(default=None)):
    context = {"req_time": req_time}

    city = await db_manager.get_city_by_name(city_name)
    if city is not None:
        response = await req_get_current_values(city.latitude, city.longitude, params, hourly=True)
        context["city_name"] = city.city_name
        context["details"] = response

    params = ['temperature_2m', 'pressure_msl', 'surface_pressure', 'wind_speed_10m', 'weather_code']
    context["params"] = params

    return templates.TemplateResponse(
        request=request, name="find_current_params.html", context=context
    )