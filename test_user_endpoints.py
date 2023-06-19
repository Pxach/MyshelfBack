import pytest
from fastapi import status
from main import app
from fastapi.testclient import TestClient

client=TestClient(app=app)

def test_sign_up():
    response=client.post('/Users', json={"username":"ser", "password":"acabc"})
    assert response.status_code==status.HTTP_201_CREATED

def test_login_successful():
    response=client.post('/token', json={"username":"newuser", "password":"abcabc"})
    assert response.status_code==status.HTTP_200_OK

def test_login_username_notfound():
    response=client.post('/token', json={"username":"auser", "password":"abcabc"})
    assert response.status_code==404

def test_login_wrong_password():
    response=client.post('/token', json={"username":"auser", "password":"aptsc"})
    assert response.status_code==401