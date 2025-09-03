from fastapi import FastAPI,Response,status,HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel          #we use pydantics to create a template of how a the data must be recieved
from typing import Optional
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from .database import engine, get_db
from .routes import users
from . import models

models.Base.metadata.create_all(bind = engine)  # Create the database tables (very important step)

app = FastAPI() # Create the FastAPI app

app.include_router(users.router)  # include the user router

#checking the database connectivity
while True:   
    try:
        conn = psycopg2.connect(host = 'localhost',database = 'Job_recommender',user = 'postgres',password = 'sudo',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connected successfully")
        break
        
    except Exception as error:
        print("Couldn't connect to database.. connection failed")
        print("error: ",error)
        time.sleep(2)