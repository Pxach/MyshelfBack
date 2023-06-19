from database import Base, engine
from models import Book, Author

print("Creating database...")

Base.metadata.create_all(engine)