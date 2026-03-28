from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_credits(db: Session, user_id: str, amount: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.credit_balance += amount
        db.commit()
        db.refresh(user)
    return user

def create_user_project(db: Session, project: schemas.ProjectCreate, user_id: str, job_id: str):
    db_project = models.Project(**project.model_dump(), user_id=user_id, id=job_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project_status(db: Session, job_id: str, status: str):
    project = db.query(models.Project).filter(models.Project.id == job_id).first()
    if project:
        project.status = status
        db.commit()
        db.refresh(project)
    return project

def get_user_projects(db: Session, user_id: str):
    return db.query(models.Project).filter(models.Project.user_id == user_id).order_by(models.Project.created_at.desc()).all()
