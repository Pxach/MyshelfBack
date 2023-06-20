from fastapi import FastAPI,status, Depends, BackgroundTasks, Security, Request
from typing import List, Union, Any
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
import logging
import models
import starlette
from fastapi_jwt_auth import AuthJWT
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import time
from datetime import datetime, timedelta
from functools import wraps
import MyExceptions

#                Session        

def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()

app=FastAPI()
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")
secretKey="cfb111cd24fcaa8e6905054506c3e2694a15569066cdba29090104deecd73223"
Algorithm= "HS256"
token_expires=15
oauth2_scheme= OAuth2PasswordBearer(tokenUrl="token")


#                Classes
    
class Token(BaseModel):
     access_token: str
     token_type:str

class TokenData(BaseModel):
     username:str or None=None

class User(BaseModel):
     username:str
     password:str

     class Config:
        orm_mode=True


class New_book(BaseModel):
    book_id:int
    title:str
    summary:str
    isbn:str
    author_id:int

    class Config:
        orm_mode=True

class updated_book(BaseModel):
    title:str
    summary:str
    isbn:str
    author_id:int

    class Config:
        orm_mode=True

class New_author(BaseModel):
    author_id:int
    name:str

    class Config:
        orm_mode=True

class updated_author(BaseModel):
    name:str

    class Config:
        orm_mode=True


#     Rate limiting

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



# 'utility functions'

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
     
#  The first page that appears
@app.get("/")
def home():
     return {"Please add '/docs' to the url"}

#                Users

# Create a user
@app.post("/Users", response_model=User, 
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=1, time_frame=60)
async def Sign_up( request:Request ,background_tasks:BackgroundTasks,user:User,db: Session=Depends(get_db)):
        try:
            db_user=db.query(models.User).filter(models.User.username==user.username).first()
            if db_user is not None:
                raise MyExceptions.redundant_user
            else:
                new_user=models.User(
                    username=user.username,
                    password=user.password,
                )

                background_tasks.add_task(db.add,new_user)
                background_tasks.add_task(db.commit)
                logging.info(f"User created")
                return new_user
        except MyExceptions.redundant_user as e:
            return e


@app.post("/token",response_model=Token, status_code=status.HTTP_200_OK)
@rate_limited(max_calls=3, time_frame=60)
async def Log_in(request:Request,form_data:OAuth2PasswordRequestForm=Depends(),db: Session=Depends(get_db)):
    try:
           db_user=db.query(models.User).filter(models.User.username==form_data.username).first()
           if db_user is None:
                raise MyExceptions.user_not_found
           else:
                if db_user.password==form_data.password:
                     access_token_expires=timedelta(minutes=token_expires)
                     access_token=createToken(data={"sub":db_user.username}, expires_delta=access_token_expires)
                     return{"access_token": access_token, "token_type":"bearer"}
                else:
                     raise MyExceptions.wrong_password
    except MyExceptions.user_not_found as e:
        return e

     
#                  books

#to print all books
@app.get("/Books", response_model=List[New_book],status_code=status.HTTP_200_OK)
@rate_limited(max_calls=2, time_frame=60)
async def List_all_books(request:Request, db: Session=Depends(get_db)):
            allbooks=db.query(models.Book).all()
            logging.info(f"all books displayed")
            return allbooks

#print books by id
@app.get("/Books/{id}",response_model=New_book,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=6, time_frame=60)
async def Find_Books_by_Id(request:Request ,id:int, db: Session=Depends(get_db)):
            try:
                found=db.query(models.Book).filter(models.Book.book_id==id).first()
                if found is None:
                    raise MyExceptions.book_not_found
                else:
                    logging.info(f"Book found")
                    return found 
            except MyExceptions.book_not_found as e:
                return e

#to create books
@app.post("/Books", response_model=New_book,
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=2, time_frame=60)
async def Create_Books(request:Request ,background_tasks:BackgroundTasks,book:New_book,db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
                try:
                        db_book=db.query(models.Book).filter(models.Book.book_id==book.book_id).first()
                        if db_book is not None:
                            raise MyExceptions.redundant_book 
                        else:
                            new_book=models.Book(
                                book_id=book.book_id,
                                title=book.title,
                                summary=book.summary,
                                isbn=book.isbn,
                                author_id=book.author_id
                            )
                        try:
                                db_author=db.query(models.Author).filter(models.Author.author_id==book.author_id).first()
                                if db_author is None:
                                    raise MyExceptions.author_not_found
                                else:
                                    background_tasks.add_task(db.add,new_book)
                                    background_tasks.add_task(db.commit)
                                    logging.info(f"Book created")
                                    return new_book
                        except author_not_found as er:
                                return er
                except redundant_book as e:
                        return e

#to update books
@app.put("/Books/{id}",response_model=updated_book,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=1, time_frame=60)
async def Update_Books(request:Request ,background_tasks:BackgroundTasks,id:int,book:updated_book, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                db_book=db.query(models.Book).filter(models.Book.book_id==id).first()
                if db_book is None:
                    raise MyExceptions.book_not_found
                else:
                    to_update=db.query(models.Book).filter(models.Book.book_id==id).first()
                    to_update.title=book.title
                    to_update.summary=book.summary
                    to_update.isbn=book.isbn
                    to_update.author_id=book.author_id
                    try:
                        db_author=db.query(models.Author).filter(models.Author.author_id==to_update.author_id).first()
                        if db_author is None:
                            raise MyExceptions.author_not_found
                        else:
                            background_tasks.add_task(db.commit)
                            logging.info(f"Book updated")
                            return to_update
                    except author_not_found as er:
                        return er
            except book_not_found as e:
                return e

#to delete books  
@app.delete("/Books/{id}", status_code=status.HTTP_200_OK)
@rate_limited(max_calls=15, time_frame=60)
async def Delete_Book(request:Request ,background_tasks:BackgroundTasks, id:int, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                to_delete=db.query(models.Book).filter(models.Book.book_id==id).first()
                if to_delete is None:
                    raise MyExceptions.book_not_found
                else:
                    background_tasks.add_task(db.delete,to_delete)
                    background_tasks.add_task(db.commit)
                    logging.info(f"Book deleted")
                    return f'Book deleted!'
            except MyExceptions.book_not_found as e:
                return e

#                                 Authors

#to print all authors
@app.get("/Authors", response_model=List[New_author],status_code=200)
@rate_limited(max_calls=2, time_frame=60)
async def List_all_authors(request:Request ,db: Session=Depends(get_db)):
            allauthors=db.query(models.Author).all()
            logging.info(f"All Authors displayed")
            return allauthors

#print authors by id
@app.get("/Authors/{id}",response_model=New_author,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=3, time_frame=60)
async def Find_Authors_by_Id(request:Request ,id:int, db: Session=Depends(get_db)):
            try:
                found=db.query(models.Author).filter(models.Author.author_id==id).first()
                if found is None:
                    raise MyExceptions.author_not_found
                else:
                    logging.info(f"Author found")
                    return found 
            except MyExceptions.author_not_found as e:
                return e
            
#to create an author
@app.post("/Authors", response_model=New_author,
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=3, time_frame=60)
async def Create_Authors(request:Request ,background_tasks:BackgroundTasks,author:New_author,db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                db_author=db.query(models.Author).filter(models.Author.author_id==author.author_id).first()
                if db_author is not None:
                    raise MyExceptions.redundant_author
                else:
                    new_author=models.Author(
                        author_id=author.author_id,
                        name=author.name,
                    )

                    background_tasks.add_task(db.add,new_author)
                    background_tasks.add_task(db.commit)
                    logging.info(f"Author created")
                    return new_author
            except MyExceptions.redundant_author as e:
                return e
        
#to update
@app.put("/Authors/{id}",response_model=updated_author,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=2, time_frame=60)
async def Update_Authors(request:Request ,background_tasks:BackgroundTasks,id:int,author:updated_author, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                db_author=db.query(models.Author).filter(models.Author.author_id==id).first()
                if db_author is None:
                    raise MyExceptions.author_not_found
                else:
                    to_update=db.query(models.Author).filter(models.Author.author_id==id).first()
                    to_update.name=author.name
                    background_tasks.add_task(db.commit)
                    logging.info(f"Author updated")
                    return to_update
            except MyExceptions.author_not_found as e:
                return e

#to delete    
@app.delete("/Authors/{id}")
@rate_limited(max_calls=2, time_frame=60)
async def Delete_Author(request:Request ,background_tasks:BackgroundTasks,id:int, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                to_delete=db.query(models.Author).filter(models.Author.author_id==id).first()
                if to_delete is None:
                    raise MyExceptions.author_not_found
                else:
                    background_tasks.add_task(db.delete,to_delete)
                    background_tasks.add_task(db.commit)
                    logging.info(f"Author deleted")
                    return f'Author deleted!'
            except MyExceptions.author_not_found as e:
                return e
            
