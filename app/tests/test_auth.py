from app.services.auth import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from jose import jwt
from app.core.config import settings


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