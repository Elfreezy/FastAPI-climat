import uvicorn
import ssl
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from .api.controller.routes import router
from .api.utils.db import metadata, database, engine
from .api.utils.service import update_weather_codes

metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполнение перед началом
    await database.connect()

    # Повторять каждые 15 минут
    scheduler = AsyncIOScheduler()
    scheduler.add_job(func=update_weather_codes, trigger='interval', seconds=60 * 15)
    scheduler.start()
    yield

    # Выполнение после завершения
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get('/')
async def root():
    return {"Message": "Hello root"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

