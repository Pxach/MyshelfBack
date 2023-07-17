from database import Base
from sqlalchemy import String,Integer, Column, Text,Boolean

class Book(Base):
    __tablename__='Books'
    book_id=Column(Integer, primary_key=True)
    title=Column(String(255),nullable=False)
    summary=Column(Text,nullable=False)
    isbn=Column(String(255),nullable=False)
    author=Column(String(225),nullable=False)


class Author(Base):
    __tablename__='Authors'
    author_id=Column(Integer, primary_key=True)
    name=Column(String(255),nullable=False)

class User(Base):
     __tablename__="Users"
     username=Column(String(255), primary_key=True)
     password=Column(String(255),nullable=False)
     isAdmin=Column(Boolean,nullable=True)
