import pytest
from fastapi import status
from main import app
from fastapi.testclient import TestClient

client=TestClient(app=app)


def test_print_all_authors():
    response=client.get('/Authors')
    assert response.status_code == status.HTTP_200_OK

def test_print_author_existing_id():
    response=client.get("/Authors/1")
    assert response.status_code==status.HTTP_200_OK

def test_print_author_nonexisting_id():
    response=client.get("/Authors/7")
    assert response.status_code==404

def test_create_author_valid():
    response=client.post("/Authors/", json={"author_id":4, "name":"sara"})
    assert response.status_code==status.HTTP_201_CREATED

def test_create_author_id_already_in_use():
    response=client.post("/Authors/", json={"author_id":1, "name":"mark"})
    assert response.status_code==400

def test_update_author_valid():
    response=client.put("/Authors/2", json={"name":"updated_name"})
    assert response.status_code==status.HTTP_200_OK

def test_update_author_nonexisting_id():
    response=client.put("/Authors/7", json={"name":"updated_name"})
    assert response.status_code==404

def test_delete_author_valid():
    response=client.delete("/Authors/3")
    assert response.status_code==status.HTTP_200_OK

def test_delete_author_nonexisting_id():
    response=client.delete("/Authors/7")
    assert response.status_code==404