from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
import json
import pytest
from devtools import debug
from httpx import AsyncClient
from pydantic import BaseSettings, BaseModel, Field
from app.app import app
from app.models.user import User
from beanie import PydanticObjectId


fake = Faker()
client = TestClient(app)

pytestmark = pytest.mark.asyncio

# NOTE: Add logout test

# Test User class
@pytest.mark.skip()
class TestUser(BaseModel):
    first_name: str = fake.first_name()
    last_name: str = fake.last_name()
    email: str = (first_name[0] + last_name + "@ucmerced.edu").lower()
    password: str = fake.password()
    id: PydanticObjectId | None = None
    token: str = ""
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

# first_name: str = fake.first_name()
# last_name: str = fake.last_name()
# email: str = (first_name[0] + last_name + "@ucmerced.edu").lower()
# password: str = fake.password()
# new_user = User(email=email, first_name=first_name, last_name=last_name, hashed_password=password)
new_user = TestUser()

# Test to see if the user can create an account
# Check if the response is 201(Success)
# Check if the user information is correct
async def test_register(client_test: AsyncClient, new_user: TestUser = new_user):
    Faker.seed(0)
    new_user = TestUser()
    # response = await client_test.get("/groups/")#, json={"email": "example@tmail.com", "password": "1234"})
    response = await client_test.post("/auth/register", json=new_user.dict())
    assert response.status_code == 201
    response = response.json()
    assert response.get("id") != None
    assert response.get("email") == new_user.email
    assert response.get("first_name") == new_user.first_name
    assert response.get("last_name") == new_user.last_name
    new_user.id= response.get("id") 
    return new_user

# Test to see if the user can register with an existing email
async def test_register_existing_email(client_test: AsyncClient):
    response = await client_test.post("/auth/register", json=new_user.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = response.json()
    assert response.get("detail") == "REGISTER_USER_ALREADY_EXISTS"

# Test to see if the new user can login with the correct credentials
async def test_login(client_test: AsyncClient, new_user: TestUser = new_user):
    response = await client_test.post("/auth/jwt/login", data={"username": new_user.email, "password": new_user.password})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response.get("token_type") == "bearer"
    assert response.get("access_token") != None
    new_user.token = response.get("access_token")
        
    # response = client.post("/auth/", headers={"X-Token": "hailhydra"})
    # assert response.status_code == 400
    # assert response.json() == {"detail": "Invalid X-Token header"}

# Test to see if the new user can login with the incorrect email
async def test_login_incorrect_username(client_test: AsyncClient):
    response = await client_test.post("/auth/jwt/login", data={"username": "incorrect_username", "password": new_user.password})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = response.json()
    assert response.get("detail") == "LOGIN_BAD_CREDENTIALS"

# Test to see if the new user can login with the incorrect password
async def test_login_incorrect_password(client_test: AsyncClient):
    response = await client_test.post("/auth/jwt/login", data={"username": new_user.email, "password": "incorrect_password"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = response.json()
    assert response.get("detail") == "LOGIN_BAD_CREDENTIALS"

# Test to see if the user can get their own information
async def test_get_account_info(client_test: AsyncClient):    
    response = await client_test.get("/users/me", headers={"Authorization": "Bearer " + new_user.token})
    assert response.status_code == 200
    response = response.json()
    assert response.get("id") == new_user.id
    assert response.get("email") == new_user.email
    assert response.get("first_name") == new_user.first_name
    assert response.get("last_name") == new_user.last_name
    assert response.get("is_active") == True
    assert response.get("is_superuser") == False
    assert response.get("is_verified") == False

# Test to see if User can delete their own account
async def test_delete_account(client_test: AsyncClient):
    # await User.update({"_id": new_user.id}, {"$set": {"is_superuser": True}})
    found_user = None
    if new_user.id:
        found_user = await User.get(new_user.id)
    if found_user:
        found_user.is_superuser = True
        await found_user.save()
    response = await client_test.delete(f"/users/{new_user.id}", headers={"Authorization": "Bearer " + new_user.token})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # assert response.status_code == status.HTTP_403_FORBIDDEN
    

# TODO: Update the user's information

    
