from fastapi import FastAPI,status, Depends, BackgroundTasks, Request
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import  timedelta
import MyExceptions
from classes import *
from Myfunctions import *
import logging
import models
import services
from fastapi.middleware.cors import CORSMiddleware
import itertools

app=FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

# "https://myshelf-11f78aafd8e0.herokuapp.com"
# "https://myshelf.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins="https://myshelf.onrender.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class iteratingIDs():
    newid = itertools.count()
     
#            The first text that appears

@app.get("/", include_in_schema=False)
def home():
    return ("Please add '/docs' to the url")


#                s
#Get current user
@app.get("/Users/{username}" ,response_model=User,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=55, time_frame=60)
async def List_current_user(request:Request, username:str,db: Session=Depends(get_db)):
            user=db.query(models.User).filter(models.User.username==username).first()
            return user

# Create a user
@app.post("/Users", response_model=User, 
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=10, time_frame=60)
async def Sign_up( request:Request ,background_tasks:BackgroundTasks,user:User,db: Session=Depends(get_db)):
        try:
            db_user=db.query(models.User).filter(models.User.username==user.username).first()
            if db_user is not None:
                raise MyExceptions.redundant_user
            else:
                new_user=models.User(
                    username=user.username,
                    password=user.password,
                    isAdmin=user.isAdmin
                )
                background_tasks.add_task(db.add,new_user)
                background_tasks.add_task(db.commit)
                logging.info(f"User created")
                return new_user
        except MyExceptions.redundant_user as e:
            return e

#  For login (does not appear)
# , include_in_schema=False
@app.post("/token",response_model=Token, status_code=status.HTTP_200_OK)
@rate_limited(max_calls=20, time_frame=60)
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
    
# , token:str=Depends(oauth2schemas)
@app.get("/Users/me", response_model=User)
async def get_user(user:User=Depends(get_current_user)):
      return user


# temp, show all users
@app.get("/Users" ,response_model=List[User],status_code=status.HTTP_200_OK)
@rate_limited(max_calls=55, time_frame=60)
async def List_all_users(request:Request, db: Session=Depends(get_db)):
            allusers=db.query(models.User).all()
            logging.info(f"all users displayed")
            return allusers


#to update users
@app.put("/Users/update/{username}",response_model=Updated_User,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=120, time_frame=60)
async def Update_User(request:Request ,background_tasks:BackgroundTasks,username:str,user:Updated_User, db: Session=Depends(get_db)):
                
                to_update=db.query(models.User).filter(models.User.username==username).first()
                to_update.isAdmin=user.isAdmin
                background_tasks.add_task(db.commit)
                logging.info(f"Author updated")
                return to_update


# #temp, delete users
# @app.delete("/Users",status_code=status.HTTP_200_OK)
# @rate_limited(max_calls=55, time_frame=60)
# async def Delete_all_users(request:Request, background_tasks:BackgroundTasks,db: Session=Depends(get_db)):
#                 to_delete=db.query(models.User).filter(models.User.username==username).first()
#                 background_tasks.add_task(db.delete,to_delete)
#                 background_tasks.add_task(db.commit)
#                 logging.info(f"user deleted")
#                 return f'user deleted!'


#                  Books

@app.get("/Books" ,response_model=List[New_book],status_code=status.HTTP_200_OK)
@rate_limited(max_calls=55, time_frame=60)
async def List_all_books(request:Request, db: Session=Depends(get_db)):
            allbooks=db.query(models.Book).all()
            logging.info(f"all books displayed")
            return allbooks

#print books by title
@app.get("/Books/{title}",response_model=List[New_book],status_code=status.HTTP_200_OK)
@rate_limited(max_calls=55, time_frame=60)
async def Find_Books_by_Id(request:Request ,title:str, db: Session=Depends(get_db)):
            try:
                # change it with like
                found=db.query(models.Book).filter((func.lower(models.Book.title)).startswith(func.lower(title))).all()
                if found==[]:
                    raise MyExceptions.book_not_found
                else:
                    logging.info(f"Book found")
                return found 
            except MyExceptions.book_not_found as e:
                return e

#to create books
@app.post("/Books", 
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=20, time_frame=60)
async def Create_Books(request:Request ,background_tasks:BackgroundTasks,book:updated_book,db: Session=Depends(get_db)):
                # try:
                #         db_book=db.query(models.Book).filter(models.Book.book_id==book.book_id).first()
                #         if db_book is not None:
                #             raise MyExceptions.redundant_book 
                #         else:
                    new_book=models.Book(
                        title=book.title,
                        summary=book.summary,
                        isbn=book.isbn,
                        author=book.author
                    )
                    background_tasks.add_task(db.add,new_book)
                    background_tasks.add_task(db.commit)
                    logging.info(f"Book created")
                    return new_book
                        # try:
                        #         db_author=db.query(models.Author).filter(models.Author.author_id==book.author_id).first()
                        #         if db_author is None:
                        #             raise MyExceptions.author_not_found
                        #         else:
                        #             background_tasks.add_task(db.add,new_book)
                        #             background_tasks.add_task(db.commit)
                        #             logging.info(f"Book created")
                        #             return new_book
                        # except MyExceptions.author_not_found as er:
                        #         return er
                # except MyExceptions.redundant_book as e:
                #         return e

#to update books
@app.put("/Books/{id}",response_model=updated_book,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=50, time_frame=60)
async def Update_Books(request:Request ,background_tasks:BackgroundTasks,id:int,book:updated_book, db: Session=Depends(get_db)):
            try:
                db_book=db.query(models.Book).filter(models.Book.book_id==id).first()
                if db_book is None:
                    raise MyExceptions.book_not_found
                else:
                    to_update=db.query(models.Book).filter(models.Book.book_id==id).first()
                    to_update.title=book.title
                    to_update.summary=book.summary
                    to_update.isbn=book.isbn
                    to_update.author=book.author
                    background_tasks.add_task(db.commit)
                    logging.info(f"Book updated")
                    return to_update
                    # try:
                    #     db_author=db.query(models.Author).filter(models.Author.author==to_update.author).first()
                    #     if db_author is None:
                    #         raise MyExceptions.author_not_found
                        # else:
                    # except MyExceptions.author_not_found as er:
                    #     return er
            except MyExceptions.book_not_found as e:
                return e

#add following in delete book ()
# ,current_user:User=Depends(get_current_user)
#to delete books  
@app.delete("/Books/{id}", status_code=status.HTTP_200_OK)
@rate_limited(max_calls=10, time_frame=60)
async def Delete_Book(request:Request ,background_tasks:BackgroundTasks, id:int, db: Session=Depends(get_db)):
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


#delete user by username
@app.delete("/Users/delete/{username}",status_code=status.HTTP_200_OK)
@rate_limited(max_calls=55, time_frame=60)
async def Delete_user(request:Request, background_tasks:BackgroundTasks,username:str, db: Session=Depends(get_db)):
                to_delete=db.query(models.User).filter(models.User.username==username).first()
                background_tasks.add_task(db.delete,to_delete)
                background_tasks.add_task(db.commit)
                logging.info(f"user deleted")
                return f'user deleted!'

#                  Authors and books
#print books by title
@app.get("/Books/written/{author}",response_model=List[New_book],status_code=status.HTTP_200_OK)
@rate_limited(max_calls=100, time_frame=60)
async def Find_Books_of_Authors(request:Request ,author:str, db: Session=Depends(get_db)):
            try:
                # change it with like
                found=db.query(models.Book).filter((func.lower(models.Book.author))==(func.lower(author))).all()
                if found==[]:
                    raise MyExceptions.book_not_found
                else:
                    logging.info(f"Book found")
                return found 
            except MyExceptions.book_not_found as e:
                return e



#                                 Authors

#to print all authors
@app.get("/Authors", response_model=List[New_author],status_code=200)
@rate_limited(max_calls=13, time_frame=60)

#current_user:User=Depends(get_current_user)
async def List_all_authors(request:Request ,db: Session=Depends(get_db)):
            allauthors=db.query(models.Author).all()
            logging.info(f"All Authors displayed")
            return allauthors

#print authors by id
@app.get("/Authors/{id}",response_model=New_author,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=3, time_frame=60)
async def Find_Authors_by_Id(request:Request ,id:int, db: Session=Depends(get_db),current_user:User=Depends(get_current_user)):
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
@app.post("/Authors", 
          status_code=status.HTTP_201_CREATED)
@rate_limited(max_calls=16, time_frame=60)
async def Create_Authors(request:Request ,background_tasks:BackgroundTasks,author:updated_author,db: Session=Depends(get_db)):
            # try:
                # db_author=db.query(models.Author).filter(models.Author.author_id==author.author_id).first()
                # if db_author is not None:
                #     raise MyExceptions.redundant_author
                # else:
            new_author=models.Author(
                 name=author.name
             )
            background_tasks.add_task(db.add,new_author)
            background_tasks.add_task(db.commit)
            logging.info(f"Author created")
            return new_author
            # except MyExceptions.redundant_author as e:
            # return e
        
#to update authors
@app.put("/Authors/{id}",response_model=updated_author,status_code=status.HTTP_200_OK)
@rate_limited(max_calls=50, time_frame=60)
async def Update_Authors(request:Request ,background_tasks:BackgroundTasks,id:int,author:updated_author, db: Session=Depends(get_db)):
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

#to delete authors
@app.delete("/Authors/{id}")
@rate_limited(max_calls=19, time_frame=60)
async def Delete_Author(request:Request ,background_tasks:BackgroundTasks,id:int, db: Session=Depends(get_db)):
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
            
