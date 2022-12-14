from faker import Faker
from fastapi.testclient import TestClient
from fastapi import status
import json
import pytest
from pydantic import BaseModel
from devtools import debug
from httpx import AsyncClient
from pydantic import BaseSettings
from app.app import app
from beanie import PydanticObjectId

from app.tests import test_users

fake = Faker()
client = TestClient(app)

pytestmark = pytest.mark.asyncio

'''
    # This test involves testing group functionality.
    ## Test 1: Create a group
    1) Create a temporary owner for test. (Success)
    2) The new user gets list of groups. (Success)
    3) The list of groups is empty. (Success)  
    4) The user creates a group. (Success)
    5) The user creates a group with the same name. (Failure)
    6) The user gets list of groups. (Success)
    7) The list of groups contains new group. (Success)
    8) The new group has the correct name, description, and the user is the owner, admin, and user. (Success)
    9) The user creates a group with the same name. (Failure)
    10) The owner adds owner to the group. (Failure)
    
    ## Test 2: Add another user to the group
    1) Create a temporary user2 for test. (Success)
    2) The new user gets list of groups. (Success)
    3) The list of groups is empty. (Success)
    4) The  user2 joins the group. (Success)
    5) The user2 adds themselves to the group. (Failure)
    6) The owner gets list of groups. (Success)
    7) The list of groups contains new group. (Success)
    8) The new group has the correct name, description, and the owner is owner, while user2 is a regular user. (Success)
    
    ## Test 3: Add another user to the group with admin permissions
    1) Create a temporary user3 for test. (Success)
    2) The new user gets list of groups. (Success)
    3) The list of groups is empty. (Success)
    4) The owner adds user3 to the group with admin permissions. (Success)
    5) The owner adds themselves to the group. (Failure)
    6) The owner gets list of groups. (Success)
    7) The list of groups contains new group. (Success)
    8) The new group has the correct name, description, and the owner is user and admin. (Success)
    
    ## Test 4: Test group permissions
    1) Create a temporary user4 for test. (Success)
    1) The user2 removes owner from the group. (Failure)
    2) The user2 removes user3 from the group. (Failure)
    3) The user2 adds user4 from the group. (Failure)
    ) The user3 adds user4 to the group. (Success)
    2) The user3 changes the group name. (Failure)
    3) The user3 changes the group description. (Failure)
    4) The user3 removes owner from the group. (Failure)

    ## Test 5: Test deleting a group
'''
# @pytest.mark.skip()
# class TestUser(BaseModel):
#     first_name: str = fake.first_name()
#     last_name: str = fake.last_name()
#     email: str = (first_name[0] + last_name + "@ucmerced.edu").lower()
#     password: str = fake.password()
#     id: PydanticObjectId | None = None
#     token: str = ""
#     is_active: bool = True
#     is_superuser: bool = False
#     is_verified: bool = False

@pytest.mark.skip()
class TestGroup(BaseModel):
    id: PydanticObjectId | None = None
    name: str = fake.company()
    description: str = fake.sentence()
    owner: PydanticObjectId | None = None
    admins: list[PydanticObjectId] = []
    members: list[PydanticObjectId] = []
    

global owner, admins, members, group
owner = test_users.TestUser()
# admins = [TestUser() for i in range(3)]
# users = [TestUser() for i in range(10)]
group = TestGroup()


async def test_create_group(client_test: AsyncClient): 
    global owner, admins, members, group
    # Register new user who will be the owner of the group
    owner = await test_users.test_register(client_test, owner)
    await test_users.test_login(client_test, owner)  # Login the user

    # Create a group
    response = await client_test.post("/groups", json={"name": group.name, "description": group.description} , headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_201_CREATED

async def test_add_user_to_group(client_test: AsyncClient):
    # Create a temporary user for test
    for i in range(len(users)):
        user_add

        # Add user to group
        response = await client_test.post("/groups/{}",
                                          json={"group_id": group.id,
                                                "user_id": users[0].id},
                                          headers={"Authorization": f"Bearer {owner.token}"})
        assert response.status_code == status.HTTP_200_OK


        


# # Test to see if the user can create an account
# async def test_root(client_test: AsyncClient):
#     # response = await client_test.get("/groups/")#, json={"email": "example@tmail.com", "password": "1234"})
#     response = await client_test.post("/auth/register", json=new_user.dict())
#     assert response.status_code == 201
#     response = response.json()
#     assert response.get("id") != None
#     assert response.get("email") == new_user.email
#     assert response.get("first_name") == new_user.first_name
#     assert response.get("last_name") == new_user.last_name
#     new_user.id = response.get("id") 
#     debug(new_user.dict())

# # Test to see if the new user can login
# async def test_login(client_test: AsyncClient):
#     response = await client_test.post("/auth/jwt/login", data={"username": new_user.email, "password": new_user.password})
#     assert response.status_code == 200
#     response = response.json()
#     assert response.get("token_type") == "bearer"
#     assert response.get("access_token") != None
#     new_user.token = response.get("access_token")
        
#     # response = client.post("/auth/", headers={"X-Token": "hailhydra"})
#     # assert response.status_code == 400
#     # assert response.json() == {"detail": "Invalid X-Token header"}
