import pytest
from fastapi import status, Security, Depends
from main import app
from fastapi.testclient import TestClient


client=TestClient(app=app)

def test_print_all_books():
    response=client.get('/Books')
    assert response.status_code == status.HTTP_200_OK

def test_print_book_existing_id():
    response=client.get("/Books/1")
    assert response.status_code==status.HTTP_200_OK
    

def test_print_book_nonexisting_id():
    response=client.get("/Books/7")
    assert response.status_code==404

def test_create_book_valid():
    response=client.post("/Books/",json={"book_id":33, "title":"new", "summary":"sum", "isbn":"an_isbn", "a_id":1})
    assert response.status_code==status.HTTP_201_CREATED
    
def test_create_book_nonexisting_author_with_given_id():
    response=client.post("/Books/", json={"book_id":7, "title":"new", "summary":"sum", "isbn":"anisbn", "a_id":7})
    assert response.status_code==404
    

def test_create_book_id_already_in_use():
    response=client.post("/Books/", json={"book_id":1, "title":"new", "summary":"sum", "isbn":"anisbn", "a_id":1})
    assert response.status_code==400
    

def test_update_book_valid():
    response=client.put("/Books/1", json={"title":"update", "summary":"update", "isbn":"update", "a_id":1},)
    assert response.status_code==status.HTTP_200_OK
    

def test_update_book_nonexisting_id():
    response=client.put("/Books/7", json={"title":"update", "summary":"update", "isbn":"update", "a_id":1},)
    assert response.status_code==404
    

def test_update_book_nonexisting_author_id():
    response=client.put("/Books/1", json={"title":"update", "summary":"update", "isbn":"update", "a_id":7},)
    assert response.status_code==404


def test_delete_book_valid():
    response=client.delete("/Books/2")
    assert response.status_code==status.HTTP_200_OK

def test_delete_book_nonexisting_id():
    response=client.delete("/Books/33")
    assert response.status_code==404

