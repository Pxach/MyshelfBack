import MyExceptions
from fastapi import Depends,Request
from datetime import datetime, timedelta
from database import SessionLocal
import models
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from classes import TokenData
from functools import wraps
import time
import logging

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")
secretKey="cfb111cd24fcaa8e6905054506c3e2694a15569066cdba29090104deecd73223"
Algorithm= "HS256"
token_expires=5
oauth2_scheme= OAuth2PasswordBearer(tokenUrl="token")


def createToken(data:dict, expires_delta: timedelta or None = None):
     to_encode=data.copy()
     if expires_delta:
          expire=datetime.utcnow() + expires_delta
     else:
          expire=datetime.utcnow() + timedelta(minutes=10)
     to_encode.update({"exp":expire})
     encoded_jwt = jwt.encode(to_encode, secretKey, algorithm=Algorithm)
     return encoded_jwt


async def get_current_user(token: str=Depends(oauth2_scheme)):
     db=next(get_db())
     try:
          payload=jwt.decode(token, secretKey, algorithms=[Algorithm])
          username:str=payload.get("sub")
          if username is None:
               raise MyExceptions.credential_exception
          token_data = TokenData(username=username)
     except JWTError:
          raise MyExceptions.credential_exception
     db_user=db.query(models.User).filter(models.User.username==token_data.username).first()
     if db_user is not None:
          return db_user
     else:
          raise MyExceptions.credential_exception
     

#                         Rate limiting

def rate_limited(max_calls:int, time_frame:int):
     def decorator(func):
          calls=[]

          @wraps(func)
          async def wrapper(request: Request, *args, **kwargs):
               now=time.time()
               calls_in_time_frame=[all for call in calls if call>now - time_frame]
               if len(calls_in_time_frame)>= max_calls:
                     logging.error("Rate limit exceeded", exc_info=True)
                     raise  MyExceptions.Exceeded_rate_limit
               calls.append(now)
               return await func(request,*args, **kwargs)
          return wrapper
     return decorator


#              Database
def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()