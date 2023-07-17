
from pydantic import BaseModel

class New_book(BaseModel):
    book_id:int
    title:str
    summary:str
    isbn:str
    author:str

    class Config:
        orm_mode=True


class User(BaseModel):
     username:str
     password:str
     isAdmin:bool


     class Config:
        orm_mode=True

class Updated_User(BaseModel):
     isAdmin:bool


     class Config:
        orm_mode=True

class updated_book(BaseModel):
    title:str
    summary:str
    isbn:str
    author:str

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
    
class Token(BaseModel):
     access_token: str
     token_type:str

class TokenData(BaseModel):
     username:str or None=None



