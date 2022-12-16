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
import random
from app.utils.colored_dbg import info 
from app.models.user import User
from app.tests import test_1_users

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


# TODO: Add a superuser test 
# TODO: Creating a large number of groups and users
# TODO: assert that a superuser can see all groups and users

@pytest.mark.skip()
def create_random_user():
    first_name = fake.first_name()
    last_name = fake.unique.last_name()
    email = (first_name[0] + last_name + "@ucmerced.edu").lower()
    password = fake.password()
    return test_1_users.TestUser(first_name=first_name, last_name=last_name, email=email, password=password)

@pytest.mark.skip()
class TestGroup(BaseModel):
    id: PydanticObjectId | None = None
    name: str = "Group " + fake.aba()
    description: str = fake.sentence()
    owner: PydanticObjectId | None = None
    admins: list[PydanticObjectId] = []
    members: list[PydanticObjectId] = []
    

global owner, admins, members, group
owner = create_random_user()
admins = [create_random_user() for i in range(3)]
users = [create_random_user() for i in range(10)]
group = TestGroup()


async def test_create_group(client_test: AsyncClient): 
    global owner, admins, members, group
    # Register new user who will be the owner of the group
    print("\n")
    owner = await test_1_users.test_register(client_test, owner)
    info("Created owner {} + {} ({})".format(owner.first_name, owner.last_name, owner.email))
    await test_1_users.test_login(client_test, owner)  # Login the user
    info("Logged in owner {} + {} ({})".format(owner.first_name, owner.last_name, owner.email))

    # Get list of groups
    response = await client_test.get("/groups", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["groups"] == []
    info("Owner has no groups")

    # Create a group
    response = await client_test.post("/groups", json={"name": group.name, "description": group.description} , headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_201_CREATED
    response = response.json()
    assert response["name"] == group.name
    group.id = response["_id"]  # Set the group id
    info("Created group {} with id {}".format(group.name, group.id))

    # Find group in user's list of groups
    response = await client_test.get("/groups", params={"name": group.name}, headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    response = response["groups"][0]  # Get the first group(should be the only group)
    assert response["name"] == group.name
    assert response["role"] == "owner"
    info("Owner has group \"{}\" with id {}".format(group.name, group.id))
    
    # Get the group and and validate basic information
    response = await client_test.get(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["description"] == group.description
    assert response["owner_name"] == owner.first_name + " " + owner.last_name
    assert response["owner_email"] == owner.email
    info("Group \"{}\" has correct name, description and owner".format(group.name))
    
    # Check that there is no admins
    # NOTE: Technically, the owner is an admin too, but this request returns members without strictly admin privilege
    response = await client_test.get(f"/groups/{group.id}/admins", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 0
    info("Group \"{}\" has no admins (except owner)".format(group.name))
    
    # Check that the owner is the only user
    # NOTE: Technically, the owner is also a user, but this request returns members with user privileges
    response = await client_test.get(f"/groups/{group.id}/users", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 0
    # temp = response["members"][0]
    # assert temp["email"] == owner.email
    # assert temp["role"] == "admin"
    info("Group \"{}\" has no users (except owner)".format(group.name))
    
    # Check that the owner is the only member
    response = await client_test.get(f"/groups/{group.id}/members", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 1
    temp = response["members"][0]
    assert temp["email"] == owner.email
    assert temp["role"] == "owner"
    info("Group \"{}\" has one member: {} ({}) - ({})".format(group.name, owner.first_name, owner.email, temp["role"]))
    
    # Get the owner of the group
    response = await client_test.get(f"/groups/{group.id}/owner", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["email"] == owner.email
    assert response["first_name"] == owner.first_name
    assert response["last_name"] == owner.last_name
    info("Group \"{}\" owner information is correct".format(group.name))
    


async def test_add_members_to_group(client_test: AsyncClient):
    print("\n")
    info("Testing adding members to group \"{}\"".format(group.name))
    members = []  # List of members to add to the group

    for i in range(len(users)):
        users[i] = await test_1_users.test_register(client_test, users[i])
        info("User {} + {} ({}) has registered".format(users[i].first_name, users[i].last_name, users[i].email))
        members.append({"email": users[i].email, "role": "user"})
        info("User {} has been added to the group list as a member".format(users[i].first_name))

    for i in range(len(admins)):
        admins[i] = await test_1_users.test_register(client_test, admins[i])
        info("User {} + {} ({}) has registered".format(users[i].first_name, users[i].last_name, users[i].email))
        members.append({"email": admins[i].email, "role": "admin"})    
        info("User {} has been added to the group list as an admin".format(users[i].first_name))

    # Post the members to the group
    response = await client_test.post(f"/groups/{group.id}/members", json={"members": members}, 
                                      headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    info("Members have been successfully added to the group")
    
    # Add owner to the members list
    members.append({"email": owner.email, "role": "owner"})
    
    # Check that all users were added to the group as members
    response = await client_test.get(f"/groups/{group.id}/members", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == len(members)
    email_list = [ member["email"] for member in response["members"]]
    for i in range(len(members)):
        assert members[i]["email"] in email_list
    info(f"The group has {len(members)} members and returned the correct list of emails")
    
    # Check that all users were added to the group as users
    response = await client_test.get(f"/groups/{group.id}/users", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == len(users)
    email_list = [ member["email"] for member in response["members"]]
    for i in range(len(users)):
        assert members[i]["email"] in email_list
    info(f"The group has {len(users)} members and returned the correct list of emails")
       
   
    # Check that all admins were added to the group as admins 
    response = await client_test.get(f"/groups/{group.id}/admins", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == len(admins)
    email_list = [ admin["email"] for admin in response["members"]]
    for i in range(len(admins)):
        assert admins[i].email in email_list
    info(f"The group has {len(admins)} admins and returned the correct list of emails")

# TODO: Test editing the group

# TODO: Test removing members from the group

# TODO: Test updating members roles

# Delete the group and users 
async def test_delete_group(client_test: AsyncClient):
    print("\n")
    info("Testing group deletion")
    # Get the group
    response = await client_test.get(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["name"] == group.name
    info(f'Group "{group.name}" exists')
    
    # Delete the group
    response = await client_test.delete(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    info(f'Group "{group.name}" has been successfully deleted')
    
    # Test to get the group
    response = await client_test.get(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    info(f'Group "{group.name}" is not found')

    # TODO: Check that no users have the group in their groups list
    

    # Delete the users by email
    await User.find({"email": {"$in": [user.email for user in (users+admins+[owner])]}}).delete()
    info("All users deleted")