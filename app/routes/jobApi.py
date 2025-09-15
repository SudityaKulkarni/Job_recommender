from .. import agents
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models
from typing import List

router = APIRouter(prefix = "/jobs", tags=["Jobs"])

@router.post("/generate-job-roles", response_model= schemas.JobRoles)
async def generate_job_roles(request:schemas.JobRequest ,db: Session = Depends(get_db)):
    get_user = db.query(models.User).filter(models.User.id == request.user_id).first()

    if not get_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "user not found -> login")

    skills = request.custom_skills.split(",") if request.custom_skills else []

    #override the skills fetched from the database if the user has provided custom skills
    if request.custom_skills:
        skills = [s.strip() for s in request.custom_skills.split(",")]

    response = await agents.get_job_roles(skills)
    if not response.roles:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Couldn't generate job roles -> try again")
    
    stringData = [s.strip() for s in ",".join(response.roles).split(",")]
    
    # Check if user already has job roles stored
    existing_job_roles = db.query(models.userJobRoles).filter(models.userJobRoles.user_id == request.user_id).first()
    
    if existing_job_roles:
        # Update existing record
        existing_job_roles.job_role = ",".join(stringData)
        db.commit()
    else:
        # Create new record
        db.add(models.userJobRoles(user_id = request.user_id, job_role = ",".join(stringData)))
        db.commit()
    
    return response


@router.get("/job-links",response_model= List[schemas.JobLinksResponse])
async def get_job_links(user_id:int, db: Session = Depends(get_db)):
    
    get_user = db.query(models.userJobRoles).filter(models.userJobRoles.user_id == user_id).first()
    
    if not get_user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No job roles found for this user -> generate job roles first")
    
    all_jobs = get_user.job_role
    all_jobs = all_jobs.split(",")
    
    all_job_links = []

    for i in all_jobs:
        jobs = await agents.get_job_links(i)       #calls adzuna api to fetch relevant job links
        all_job_links.append({"job_role": i, "jobs": jobs})

    return all_job_links
