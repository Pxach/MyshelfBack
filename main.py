from fastapi import FastAPI,status, HTTPException,Depends, BackgroundTasks, Security, Request
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
TokenExpires=15
oauth2_scheme= OAuth2PasswordBearer(tokenUrl="token")


#            Exceptions
     
class Booknotfound(Exception):
    "Exception raised when the book entered does not exist. "
    def __init__(self):
        logging.error("Book not found", exc_info=True)
        raise HTTPException(status_code=404,
                                detail=f'Book does not exist')
    pass

class Redundantbook(Exception):
    "Exception raised when the book to create already exists. "
    def __init__(self):
        logging.error("Book already exists", exc_info=True)
        raise HTTPException(status_code=400,
                                detail=f'Book already exists')
    pass

class Authornotfound(Exception):
    "Exception raised when the author entered does not exist. "
    def __init__(self):
        logging.error("Author not found", exc_info=True)
        raise HTTPException(status_code=404,
                                detail=f'Author does not exist')
    pass

class Redundantauthor(Exception):
    "Exception raised when the author to create already exists. "
    def __init__(self):
        logging.error("Author already exists", exc_info=True)
        raise HTTPException(status_code=400,
                                detail=f'Author already exists')
    pass

class Redundantuser(Exception):
    "Exception raised when the user to create already exists. "
    def __init__(self):
        logging.error("User already exists", exc_info=True)
        raise HTTPException(status_code=400,
                                detail=f'username already exists')
    pass
class Usernotfound(Exception):
    "Exception raised when the user entered does not exist. "
    def __init__(self):
        logging.error("User not found", exc_info=True)
        raise HTTPException(status_code=404,
                                detail=f'User does not exist')
    pass
class Wrongpassword(Exception):
    "Exception raised when the password entered is wrong. "
    def __init__(self):
        logging.error("Invalid username or password", exc_info=True)
        raise HTTPException(status_code=401,
                                detail=f'Invalid username or password')
    pass



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


class Newbook(BaseModel):
    book_id:int
    title:str
    summary:str
    isbn:str
    a_id:int

    class Config:
        orm_mode=True

class updatedbook(BaseModel):
    title:str
    summary:str
    isbn:str
    a_id:int

    class Config:
        orm_mode=True

class Newauthor(BaseModel):
    author_id:int
    name:str

    class Config:
        orm_mode=True

class updatedauthor(BaseModel):
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
                     raise  HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
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
     credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
     try:
          payload=jwt.decode(token, secretKey, algorithms=[Algorithm])
          username:str=payload.get("sub")
          if username is None:
               raise credential_exception
          token_data = TokenData(username=username)
     except JWTError:
          raise credential_exception
     db_user=db.query(models.User).filter(models.User.username==token_data.username).first()
     if db_user is not None:
          return db_user
     else:
          raise credential_exception
     


#                Users

# Create a user
@app.post("/Users", response_model=User, 
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=1, time_frame=60)
async def Sign_up( request:Request ,background_tasks:BackgroundTasks,user:User,db: Session=Depends(get_db)):
        try:
            db_user=db.query(models.User).filter(models.User.username==user.username).first()
            if db_user is not None:
                raise Redundantuser
            else:
                new_user=models.User(
                    username=user.username,
                    password=user.password,
                )

                background_tasks.add_task(db.add,new_user)
                background_tasks.add_task(db.commit)
                logging.info(f"User created")
                return new_user
        except Redundantuser as e:
            return e


@app.post("/token",response_model=Token, status_code=status.HTTP_200_OK)
@rate_limited(max_calls=3, time_frame=60)
async def Log_in(request:Request,form_data:OAuth2PasswordRequestForm=Depends(),db: Session=Depends(get_db)):
    try:
           db_user=db.query(models.User).filter(models.User.username==form_data.username).first()
           if db_user is None:
                raise Usernotfound
           else:
                if db_user.password==form_data.password:
                     access_token_expires=timedelta(minutes=TokenExpires)
                     access_token=createToken(data={"sub":db_user.username}, expires_delta=access_token_expires)
                     return{"access_token": access_token, "token_type":"bearer"}
                else:
                     raise Wrongpassword
    except Usernotfound as e:
        return e

     

     
#                  books

#to print all books
@app.get("/Books", response_model=List[Newbook],status_code=status.HTTP_200_OK)
@rate_limited(max_calls=2, time_frame=60)
async def listAllBooks(request:Request, db: Session=Depends(get_db)):
            allbooks=db.query(models.Book).all()
            logging.info(f"all books displayed")
            return allbooks

#print books by id
@app.get("/Books/{id}",response_model=Newbook,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=6, time_frame=60)
async def FindBooksbyId(request:Request ,id:int, db: Session=Depends(get_db)):
            try:
                found=db.query(models.Book).filter(models.Book.book_id==id).first()
                if found is None:
                    raise Booknotfound
                else:
                    logging.info(f"Book found")
                    return found 
            except Booknotfound as e:
                return e

#to create books
@app.post("/Books", response_model=Newbook,
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=2, time_frame=60)
async def CreateBooks(request:Request ,background_tasks:BackgroundTasks,book:Newbook,db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
                try:
                        db_book=db.query(models.Book).filter(models.Book.book_id==book.book_id).first()
                        if db_book is not None:
                            raise Redundantbook 
                        else:
                            new_book=models.Book(
                                book_id=book.book_id,
                                title=book.title,
                                summary=book.summary,
                                isbn=book.isbn,
                                a_id=book.a_id
                            )
                        try:
                                db_author=db.query(models.Author).filter(models.Author.author_id==book.a_id).first()
                                if db_author is None:
                                    raise Authornotfound
                                else:
                                    background_tasks.add_task(db.add,new_book)
                                    background_tasks.add_task(db.commit)
                                    logging.info(f"Book created")
                                    return new_book
                        except Authornotfound as er:
                                return er
                except Redundantbook as e:
                        return e

#to update books
@app.put("/Books/{id}",response_model=updatedbook,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=1, time_frame=60)
async def UpdateBooks(request:Request ,background_tasks:BackgroundTasks,id:int,book:updatedbook, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                db_book=db.query(models.Book).filter(models.Book.book_id==id).first()
                if db_book is None:
                    raise Booknotfound
                else:
                    toupdate=db.query(models.Book).filter(models.Book.book_id==id).first()
                    toupdate.title=book.title
                    toupdate.summary=book.summary
                    toupdate.isbn=book.isbn
                    toupdate.a_id=book.a_id
                    try:
                        db_author=db.query(models.Author).filter(models.Author.author_id==toupdate.a_id).first()
                        if db_author is None:
                            raise Authornotfound
                        else:
                            background_tasks.add_task(db.commit)
                            logging.info(f"Book updated")
                            return toupdate
                    except Authornotfound as er:
                        return er
            except Booknotfound as e:
                return e

#to delete books  
@app.delete("/Books/{id}", status_code=status.HTTP_200_OK)
@rate_limited(max_calls=15, time_frame=60)
async def deleteBook(request:Request ,background_tasks:BackgroundTasks, id:int, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                todelete=db.query(models.Book).filter(models.Book.book_id==id).first()
                if todelete is None:
                    raise Booknotfound
                else:
                    background_tasks.add_task(db.delete,todelete)
                    background_tasks.add_task(db.commit)
                    logging.info(f"Book deleted")
                    return f'Book deleted!'
            except Booknotfound as e:
                return e

#                                 authors

#to print all authors
@app.get("/Authors", response_model=List[Newauthor],status_code=200)
@rate_limited(max_calls=2, time_frame=60)
async def listAllauthors(request:Request ,db: Session=Depends(get_db)):
            allauthors=db.query(models.Author).all()
            logging.info(f"All Authors displayed")
            return allauthors

#print authors by id
@app.get("/Authors/{id}",response_model=Newauthor,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=3, time_frame=60)
async def FindAuthorsbyId(request:Request ,id:int, db: Session=Depends(get_db)):
            try:
                found=db.query(models.Author).filter(models.Author.author_id==id).first()
                if found is None:
                    raise Authornotfound
                else:
                    logging.info(f"Author found")
                    return found 
            except Authornotfound as e:
                return e
            
#to create an author
@app.post("/Authors", response_model=Newauthor,
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=3, time_frame=60)
async def CreateAuthors(request:Request ,background_tasks:BackgroundTasks,author:Newauthor,db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                db_author=db.query(models.Author).filter(models.Author.author_id==author.author_id).first()
                if db_author is not None:
                    raise Redundantauthor
                else:
                    new_author=models.Author(
                        author_id=author.author_id,
                        name=author.name,
                    )

                    background_tasks.add_task(db.add,new_author)
                    background_tasks.add_task(db.commit)
                    logging.info(f"Author created")
                    return new_author
            except Redundantauthor as e:
                return e
        
#to update
@app.put("/Authors/{id}",response_model=updatedauthor,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=2, time_frame=60)
async def UpdateAuthors(request:Request ,background_tasks:BackgroundTasks,id:int,author:updatedauthor, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                db_author=db.query(models.Author).filter(models.Author.author_id==id).first()
                if db_author is None:
                    raise Authornotfound
                else:
                    toupdate=db.query(models.Author).filter(models.Author.author_id==id).first()
                    toupdate.name=author.name
                    background_tasks.add_task(db.commit)
                    logging.info(f"Author updated")
                    return toupdate
            except Authornotfound as e:
                return e

#to delete    
@app.delete("/Authors/{id}")
@rate_limited(max_calls=2, time_frame=60)
async def deleteAuthor(request:Request ,background_tasks:BackgroundTasks,id:int, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
            try:
                todelete=db.query(models.Author).filter(models.Author.author_id==id).first()
                if todelete is None:
                    raise Authornotfound
                else:
                    background_tasks.add_task(db.delete,todelete)
                    background_tasks.add_task(db.commit)
                    logging.info(f"Author deleted")
                    return f'Author deleted!'
            except Authornotfound as e:
                return e
            

