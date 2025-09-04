from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from .. import schemas,models,utils
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    #auth logic

    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    #if the username itself is invalid then we raise an exception without proceeding further for password verification
    if user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Invalid credentials")
    

    #verifying if the hashed password matches the password in the database
    #the hashing is handled by bcrypt so we dont need to hash the input password ourselves 
    passwd = utils.verify(credentials.password, user.password)

    if not passwd:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Invalid credentials")
    
    #now we create the access token and then return it to the client
    return {"access token granted"}
