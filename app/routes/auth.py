from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from .. import schemas,models,utils, oauth2
from sqlalchemy.orm import Session
from ..database import get_db

from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #auth logic

    user = db.query(models.User).filter(models.User.email == credentials.username).first()

    #if the username itself is invalid then we raise an exception without proceeding further for password verification
    if user is None:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Invalid credentials")
    

    #verifying if the hashed password matches the password in the database
    #the hashing is handled by bcrypt so we dont need to hash the input password ourselves 
    passwd = utils.verify(credentials.password, user.password)

    if not passwd:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Invalid credentials")

    #now we create the access token and then return it to the client
    access_token = oauth2.create_access_token({"user_id": user.id})
    return {"access-token": access_token, "token type":"bearer"}
