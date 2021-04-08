from sqlalchemy.orm import Session

import src.models.userModels as models
import src.schema.userSchema as schemas
import src.utils.crypt as crypt

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email_or_username(db: Session, email: str, username:str):
    return db.query(models.User).filter((models.User.email == email)| (models.User.username == username)).first()

def get_user_by_username(db:Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = crypt.create_crypt_password(user.password)
    db_user = models.User(username=user.username,email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
