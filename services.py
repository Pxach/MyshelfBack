from fastapi import FastAPI,status, Depends, BackgroundTasks, Request
from typing import List
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import  timedelta
import MyExceptions
from classes import *
from Myfunctions import *
import logging
import models



async def authenticate(username:str,password:str,db: Session=Depends(get_db)):
            db_user=db.query(models.User).filter(models.User.username==username).first()
            if not db_user:
                    return False
            if db_user.password!=password:
                    return False
            return db_user