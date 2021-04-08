from fastapi import FastAPI 
import uvicorn
from typing import List
from fastapi import Depends, FastAPI, HTTPException,Header
from sqlalchemy.orm import Session
from src.databases.connection import SessionLocal, engine
import src.models.userModels as models 
import src.schema.userSchema as schemas
import src.databases.userDatabase as crud
import src.utils.crypt as crypt
import time
import datetime as dt
import jwt

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_token(Authorization: str = Header(...),db: Session = Depends(get_db)):
    try:
        decode = jwt.decode(Authorization.replace("Bearer ",''),"segredo",algorithms="HS256",verify=True)
        user = crud.get_user(db=db,user_id=decode.get('id'))
        if not user or not user.is_active:
            raise HTTPException(status_code=400, detail="User invalid")
    except:
        raise HTTPException(status_code=400, detail="Token header invalid")
    return decode.get('id')

@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.get("/users/me",response_model=schemas.User)
async def get_user(user_id :int = Depends(verify_token),db: Session = Depends(get_db)):
    user = crud.get_user(db=db, user_id=user_id)
    return user

@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email_or_username(db, email=user.email,username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User],dependencies=[Depends(verify_token)])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/login/", response_model= schemas.UserToken)
async def user_login(user: schemas.UserLogin,db:Session =Depends(get_db)):
    db_user = crud.get_user_by_username(db=db,username=user.username)
    if crypt.verify_crypt_password(user.password, db_user.hashed_password):
        #expirationTime = int(time.time() + 36000000)
        expirationTime = int((dt.datetime.utcnow()+ dt.timedelta(weeks=24)).timestamp())
        token = jwt.encode({'id':db_user.id,'username':db_user.username,'email':db_user.email,"exp": expirationTime}, "segredo", algorithm="HS256")
        return schemas.UserToken(username=db_user.username,email=db_user.email,token=token,expireted_at=dt.datetime.fromtimestamp(expirationTime).strftime('%d-%m-%Y'))
    else:
        return {"Incorrect password!"}

