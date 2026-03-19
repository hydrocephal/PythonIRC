from app.services.auth import verify_password, get_password_hash, create_access_token, create_user, login_user
from datetime import timedelta
from jose import jwt
from app.core.config import settings
from app.schemas.auth import UserCreate


def test_password_hash_and_verify():
    password = "supersecretpass"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True

def test_create_access_token():
    username = "incorrectuser"
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
    
    assert isinstance(access_token, str)
    
    payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("sub") == username

def test_create_user(db):
    user_data = UserCreate(username="Pupok", password="pass")
    register_func = create_user(user_data, db)
    assert register_func is not None
    assert "access_token" in register_func
    assert register_func["token_type"] == "bearer"

def test_login_user(db):
    user_data = UserCreate(username="Pupok", password="pass")
    create_user(user_data, db)

    user_login = login_user(user_data.username, user_data.password, db=db)

    assert user_login is not None
    assert "access_token" in user_login
    assert user_login["token_type"] == "bearer"