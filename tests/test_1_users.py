from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
import pytest
# from devtools import debug
from httpx import AsyncClient
from pydantic import BaseModel
from beanie import PydanticObjectId
from app.app import app
from app.models.user import User
from app.utils import colored_dbg


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
    print("\n")
    colored_dbg.test_info("Registering new user: ", new_user.email)
    response = await client_test.post("/auth/register", json=new_user.dict())
    assert response.status_code == 201
    response = response.json()
    assert response.get("id") is not None
    assert response.get("email") == new_user.email
    assert response.get("first_name") == new_user.first_name
    assert response.get("last_name") == new_user.last_name
    new_user.id = response.get("id")
    colored_dbg.test_success("New user has been registered: ", new_user.email, "with id: ", new_user.id)
    return new_user


# Test to see if the user can register with an existing email
async def test_register_existing_email(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Attempting to register a new user with an existing email: ", new_user.email)
    response = await client_test.post("/auth/register", json=new_user.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = response.json()
    assert response.get("detail") == "REGISTER_USER_ALREADY_EXISTS"
    colored_dbg.test_success("The new user failed to register because email already exists: ", new_user.email)


# Test to see if the new user can login with the incorrect email
async def test_login_incorrect_username(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Attempting to login with incorrect email")
    response = await client_test.post("/auth/jwt/login",
                                      data={"username": "incorrect_username", "password": new_user.password})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = response.json()
    assert response.get("detail") == "LOGIN_BAD_CREDENTIALS"
    colored_dbg.test_success('The new user received a 404 "LOGIN_BAD_CREDENTIALS" error')


# Test to see if the new user can login with the incorrect password
async def test_login_incorrect_password(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Attempting to login with incorrect password")
    response = await client_test.post("/auth/jwt/login",
                                      data={"username": new_user.email, "password": "incorrect_password"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = response.json()
    assert response.get("detail") == "LOGIN_BAD_CREDENTIALS"
    colored_dbg.test_success('The new user received a 404 "LOGIN_BAD_CREDENTIALS" error')


# Test to see if the new user can login with the correct credentials
async def test_login(client_test: AsyncClient, new_user: TestUser = new_user):
    print("\n")
    colored_dbg.test_info("Logging in new user with correct credentials: ", new_user.email)
    response = await client_test.post("/auth/jwt/login",
                                      data={"username": new_user.email, "password": new_user.password})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response.get("token_type") == "bearer"
    assert response.get("access_token") is not None
    new_user.token = response.get("access_token")
    colored_dbg.test_success("New user has successfully logged in and received a token: ", new_user.token)


# Test to see if the user can get their own information
async def test_get_account_info(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Getting new user's account information")
    response = await client_test.get("/users/me", headers={"Authorization": "Bearer " + new_user.token})
    assert response.status_code == 200
    response = response.json()
    assert response.get("id") == new_user.id
    assert response.get("email") == new_user.email
    assert response.get("first_name") == new_user.first_name
    assert response.get("last_name") == new_user.last_name
    assert response.get("is_active") is True
    assert response.get("is_superuser") is False
    assert response.get("is_verified") is False
    colored_dbg.test_success("New user's account information has been retrieved and verified")


# Test to see if User can delete their own account
async def test_delete_account(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Deleting new user's account")
    # await User.update({"_id": new_user.id}, {"$set": {"is_superuser": True}})
    found_user = None
    if new_user.id:
        found_user = await User.get(new_user.id)
    if found_user:
        found_user.is_superuser = True
        await found_user.save()
    response = await client_test.delete(f"/users/{new_user.id}", headers={"Authorization": "Bearer " + new_user.token})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    colored_dbg.test_success("New user's account has been deleted")

# TODO: Update the user's information
# TODO: Get user's group list
