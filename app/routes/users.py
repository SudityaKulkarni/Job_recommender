from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter
from typing import List

from app import schemas
from .. import models, oauth2
from sqlalchemy.orm import Session
from ..database import get_db

from .. import utils

router = APIRouter(prefix = "/users")

#get all users
@router.get("/",status_code = status.HTTP_302_FOUND, response_model = schemas.UserResponse)
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    for user in users:
        user.skills = user.skills.split(",")
    return users

#create a user
@router.post("/create-user",status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    #hashing password
    hashed_password = utils.hash(user.password)         #importing from utils.py
    user.password = hashed_password

    db_user = models.User(**user.dict())
    db_user.skills = ",".join(user.skills)  # Convert list of skills to comma-separated string for DB
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.skills = db_user.skills.split(",")  # Convert string back to list for response
    return db_user

#get a single user by id
@router.get("/{user_id}",status_code = status.HTTP_302_FOUND,response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if(user_id != current_user.id):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Not authorized to view this user")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.skills = user.skills.split(",")
    return user

#update a user of that specific id
@router.put("/update-user/{user_id}", status_code = status.HTTP_202_ACCEPTED, response_model = schemas.UserResponse)
def update_user(user_id:int, user : schemas.UserBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if(user_id != current_user.id):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Not authorized to update this user")
    
    db_user_query = db.query(models.User).filter(models.User.id == user_id)
    db_user = db_user_query.first()
    db_user.skills = ",".join(user.skills)  # Convert list to string
    if db_user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'user not found')
    
    db_user_query.update(user.dict(),synchronize_session=False)
    db.commit()
    db.refresh(db_user)
    db_user.skills = db_user.skills.split(",")

    return db_user

#delete the user of that specified id
@router.delete("/delete-user/{user_id}", status_code = status.HTTP_204_NO_CONTENT)
def del_user(user_id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if(user_id != current_user.id):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Not authorized to delete this user")
    
    db_user = db.query(models.User).filter(models.User.id == user_id)
    if db_user.first() is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'user not found')
    
    db_user.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    