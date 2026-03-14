from app.schemas.auth import UserCreate
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.models import User
from app.core.config import settings
import bcrypt

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_user(user_data: UserCreate, db: Session):
    if db.query(User).filter(User.username == user_data.username).first():
        return None
    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_password)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        return None

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": new_user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

def login_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

