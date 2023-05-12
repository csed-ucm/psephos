from faker import Faker
from fastapi.testclient import TestClient
from fastapi import status
# import json
import pytest
from pydantic import BaseModel
# from devtools import debug
from httpx import AsyncClient
# from pydantic import BaseSettings
from app.app import app
from app.utils import colored_dbg
from app.models.account import User
from app.schemas.account import UserID
from app.schemas.group import GroupID
# from app.exceptions.group import GroupNotFound
from tests import test_1_users

fake = Faker()
client = TestClient(app)

# TODO: Add settings for testing, i.e. testing database
# class Settings(BaseSettings):

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
    id: GroupID | None = None
    name: str = "Group " + fake.aba()
    description: str = fake.sentence()
    owner: UserID | None = None
    admins: list[UserID] = []
    members: list[UserID] = []


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
    colored_dbg.test_success("Created owner {} {} ({})".format(
        owner.first_name, owner.last_name, owner.email))
    await test_1_users.test_login(client_test, owner)  # Login the user
    colored_dbg.test_success("Logged in owner {} {} ({})".format(
        owner.first_name, owner.last_name, owner.email))

    # Get list of groups
    response = await client_test.get("/groups", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["groups"] == []
    colored_dbg.test_success("Owner has no groups")

    # Create a group
    response = await client_test.post("/groups",
                                      json={"name": group.name, "description": group.description},
                                      headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_201_CREATED
    response = response.json()
    assert response["name"] == group.name
    group.id = response["id"]  # Set the group id
    colored_dbg.test_info("Created group {} with id {}".format(group.name, group.id))

    # Find group in user's list of groups
    response = await client_test.get("/groups",
                                     params={"name": group.name},
                                     headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    # Get the first group(should be the only group)
    assert len(response["groups"]) == 1
    response = response["groups"][0]
    assert response["name"] == group.name
    assert response["role"] == "owner"
    colored_dbg.test_info("Owner has group \"{}\" with id {}".format(group.name, group.id))

    # Get the group and and validate basic information
    response = await client_test.get(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["description"] == group.description
    assert response["owner_name"] == owner.first_name + " " + owner.last_name
    assert response["owner_email"] == owner.email
    colored_dbg.test_info("Group \"{}\" has correct name, description and owner".format(group.name))

    # Check that there is no admins
    # NOTE: Technically, the owner is an admin too, but this request returns members without strictly admin privilege
    response = await client_test.get(f"/groups/{group.id}/admins", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 0
    colored_dbg.test_info("Group \"{}\" has no admins (except owner)".format(group.name))

    # Check that the owner is the only user
    # NOTE: Technically, the owner is also a user, but this request returns members with user privileges
    response = await client_test.get(f"/groups/{group.id}/users", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 0
    # temp = response["members"][0]
    # assert temp["email"] == owner.email
    # assert temp["role"] == "admin"
    colored_dbg.test_info("Group \"{}\" has no users (except owner)".format(group.name))

    # Check that the owner is the only member
    response = await client_test.get(f"/groups/{group.id}/members", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 1
    temp = response["members"][0]
    assert temp["email"] == owner.email
    assert temp["role"] == "owner"
    colored_dbg.test_info("Group \"{}\" has one member: {} ({}) - ({})".format(group.name,
                                                                               owner.first_name,
                                                                               owner.email,
                                                                               temp["role"]))

    # Get the owner of the group
    response = await client_test.get(f"/groups/{group.id}/owner", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["email"] == owner.email
    assert response["first_name"] == owner.first_name
    assert response["last_name"] == owner.last_name
    colored_dbg.test_info("Group \"{}\" owner information is correct".format(group.name))


async def test_add_members_to_group(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Testing adding members to group \"{}\"".format(group.name))
    members = []  # List of members to add to the group

    for i in range(len(users)):
        users[i] = await test_1_users.test_register(client_test, users[i])
        colored_dbg.test_info("User {} + {} ({}) has registered".format(
            users[i].first_name, users[i].last_name, users[i].email))
        members.append({"email": users[i].email, "role": "user"})
        colored_dbg.test_info("User {} has been added to the group list as a member".format(
            users[i].first_name))

    for i in range(len(admins)):
        admins[i] = await test_1_users.test_register(client_test, admins[i])
        colored_dbg.test_info("User {} + {} ({}) has registered".format(
            users[i].first_name, users[i].last_name, users[i].email))
        members.append({"email": admins[i].email, "role": "admin"})
        colored_dbg.test_info("User {} has been added to the group list as an admin".format(
            users[i].first_name))

    # Post the members to the group
    response = await client_test.post(f"/groups/{group.id}/members", json={"members": members},
                                      headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_201_CREATED
    colored_dbg.test_info("Members have been successfully added to the group")

    # Add owner to the members list
    members.append({"email": owner.email, "role": "owner"})

    # Check that all users were added to the group as members
    response = await client_test.get(f"/groups/{group.id}/members", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == len(members)
    email_list = [member["email"] for member in response["members"]]
    for i in range(len(members)):
        assert members[i]["email"] in email_list
    colored_dbg.test_info(
        f"The group has {len(members)} members and returned the correct list of emails")

    # Check that all users were added to the group as users
    response = await client_test.get(f"/groups/{group.id}/users", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == len(users)
    email_list = [member["email"] for member in response["members"]]
    for i in range(len(users)):
        assert members[i]["email"] in email_list
    colored_dbg.test_info(
        f"The group has {len(users)} members and returned the correct list of emails")

    # Check that all admins were added to the group as admins
    response = await client_test.get(f"/groups/{group.id}/admins", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == len(admins)
    email_list = [admin["email"] for admin in response["members"]]
    for i in range(len(admins)):
        assert admins[i].email in email_list
    colored_dbg.test_info(
        f"The group has {len(admins)} admins and returned the correct list of emails")

# TODO: Test editing the group

# TODO: Test removing members from the group

# TODO: Test updating members roles


# Attempt to delete a user from non existing group
async def test_delete_group_no_owner(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Testing group deletion from non existing group")

    random_group_id = GroupID()

    # Delete the group
    # NOTE: pytest.raises() does not work(with async functions?)
    # with pytest.raises(GroupNotFound):
    #     response = await client_test.delete(f"/groups/{random_group_id}",
    #                                         headers={"Authorization": f"Bearer {owner.token}"})
    #     print(response.json())
    response = await client_test.delete(f"/groups/{random_group_id}",
                                        headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f'Group with id {str(random_group_id)} not found'

    colored_dbg.test_success("Group deletion from non existing group failed as expected")
    # assert response.status_code == status.HTTP_404_NOT_FOUND
    # assert


# Delete the group and users
async def test_delete_group(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Testing group deletion")
    # Get the group
    response = await client_test.get(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["name"] == group.name
    colored_dbg.test_info(f'Group "{group.name}" exists')

    # Delete the group
    response = await client_test.delete(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    colored_dbg.test_info(f'Group "{group.name}" has been successfully deleted')

    # Test to get the group
    response = await client_test.get(f"/groups/{group.id}", headers={"Authorization": f"Bearer {owner.token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    colored_dbg.test_info(f'Group "{group.name}" is not found')

    # TODO: Check that no users have the group in their groups list

    # Delete the users by email
    await User.find({"email": {"$in": [user.email for user in (users+admins+[owner])]}}).delete()
    colored_dbg.test_info("All users deleted")
