#pip install python-jose[cryptography]
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from . import schemas, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import database 

load_dotenv() # Loads environment variables from .env file
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
#SECRET KEY
#ALGORITHM
#EXPIRATION TIME

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRATION_TIME_MINS = os.getenv("EXPIRATION_TIME_MINS")


def create_access_token(data:dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes = int(EXPIRATION_TIME_MINS))

    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode,SECRET_KEY, algorithm = ALGORITHM)

    return encoded_jwt



def verify_access_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        id:str = payload.get("user_id")

        if id is None:                          # Check if user_id is present
            raise credentials_exception
        
        token_data = schemas.TokenData(id=str(id)) #create a TokenData object and return it

    except JWTError:
        raise credentials_exception

    return token_data 


def get_current_user(token:str = Depends(oauth2_scheme) ,db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code= status.HTTP_401_UNAUTHORIZED ,detail = f"could not validate credentials",headers={"WWW-Authenticate":"Bearer"})

    token = verify_access_token(token,credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user