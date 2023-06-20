from fastapi import status, HTTPException
import logging

class book_not_found(Exception):
    "Exception raised when the book entered does not exist. "
    def __init__(self):
        logging.error("Book not found", exc_info=True)
        raise HTTPException(status_code=404,
                                detail=f'Book does not exist')
    pass

class redundant_book(Exception):
    "Exception raised when the book to create already exists. "
    def __init__(self):
        logging.error("Book already exists", exc_info=True)
        raise HTTPException(status_code=400,
                                detail=f'Book already exists')
    pass

class author_not_found(Exception):
    "Exception raised when the author entered does not exist. "
    def __init__(self):
        logging.error("Author not found", exc_info=True)
        raise HTTPException(status_code=404,
                                detail=f'Author does not exist')
    pass

class redundant_author(Exception):
    "Exception raised when the author to create already exists. "
    def __init__(self):
        logging.error("Author already exists", exc_info=True)
        raise HTTPException(status_code=400,
                                detail=f'Author already exists')
    pass

class redundant_user(Exception):
    "Exception raised when the user to create already exists. "
    def __init__(self):
        logging.error("User already exists", exc_info=True)
        raise HTTPException(status_code=400,
                                detail=f'username already exists')
    pass
class user_not_found(Exception):
    "Exception raised when the user entered does not exist. "
    def __init__(self):
        logging.error("User not found", exc_info=True)
        raise HTTPException(status_code=404,
                                detail=f'User does not exist')
    pass
class wrong_password(Exception):
    "Exception raised when the password entered is wrong. "
    def __init__(self):
        logging.error("Invalid username or password", exc_info=True)
        raise HTTPException(status_code=401,
                                detail=f'Invalid username or password')
    pass

class Exceeded_rate_limit(Exception):
    "Exception raised when the rate limit was exceeded. "
    def __init__(self):
        logging.error("Rate limit exceeded", exc_info=True)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    pass


class credential_exception(Exception):
    "Exception raised when the credentials entered could not be validated"
    def __init__(self):
        logging.error("Invalid credentials", exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    pass