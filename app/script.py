import uvicorn
import ssl
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from .api.routes import router
from .api.db import metadata, database, engine
from .api.service import update_weather_codes

metadata.create_all(engine)

app = FastAPI()

app.include_router(router)


@app.get('/')
async def root():
    return {"Message": "Hello root"}


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("startup")
@repeat_every(seconds=60 * 15)  # 15 минут
async def start_task():
    await update_weather_codes()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

