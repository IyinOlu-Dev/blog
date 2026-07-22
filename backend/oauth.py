import os
from dotenv import load_dotenv
from uuid import UUID

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.model import UserModel

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_acess_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_current_user(token: str = Depends(oauth2_scheme), db: Session= Depends(get_db)):
    
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "Could not validate credentials",
        headers= {"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user= db.query(UserModel). filter(UserModel.id == UUID(user_id)).first()
    
    if user is None:
        raise credentials_exception
    
    return user