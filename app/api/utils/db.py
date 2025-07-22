import os
from typing import List
from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table,
                        create_engine, ARRAY, Float, ForeignKey)
from sqlalchemy.orm import Mapped, relationship
from databases import Database

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.getenv('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'app.db')

engine = create_engine(DATABASE_URI, connect_args={"check_same_thread": False})
metadata = MetaData()


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(16), unique=True, nullable=False),
    Column("nickname", String(50), nullable=True),
    Column("password_hash", String(100), nullable=False),
)

city = Table(
    "city",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("city_name", String(60), nullable=False),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("weather_code", Integer),
    Column("user_id", ForeignKey(user.c.id)),
)

database = Database(DATABASE_URI)



