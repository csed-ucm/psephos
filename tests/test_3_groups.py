from faker import Faker
from fastapi.testclient import TestClient
from fastapi import status
# import json
import pytest
from pydantic import BaseModel
# from devtools import debug
from httpx import AsyncClient
from beanie.operators import In
# from pydantic import BaseSettings
from unipoll_api import app
from unipoll_api.utils import colored_dbg
from unipoll_api.documents import Account, ResourceID
# from app.exceptions.group import GroupNotFound
import test_1_accounts
from test_2_workspaces import create_random_user, TestWorkspace
from unipoll_api.utils import permissions as Permissions

# import pytest
# from faker import Faker
# from fastapi.testclient import TestClient
# from fastapi import status
# from pydantic import BaseModel
# from httpx import AsyncClient
# from beanie.operators import In
# from app.app import app
# from app.utils import colored_dbg
# from app.models.documents import ResourceID, Account
# # from app.schemas import group as WorkspaceSchema
# from unipoll_api. import test_1_accounts
# from app.utils import permissions as Permissions


fake = Faker()
client = TestClient(app)  # type: ignore

# TODO: Add settings for testing, i.e. testing database
# class Settings(BaseSettings):

pytestmark = pytest.mark.asyncio


@pytest.mark.skip()
class TestGroup(BaseModel):
    id: ResourceID | None = None
    name: str = "Group " + fake.aba()
    description: str = fake.sentence()
    members: list[ResourceID] = []
    groups: list[ResourceID] = []
    policies: list[ResourceID] = []


global accounts, workspace, groups
accounts = [create_random_user() for _ in range(20)]
workspace = TestWorkspace(name="Class CSE" + fake.aba(), description=fake.sentence())
groups = [TestGroup(name="Teachers", description="Teachers of the course"),
          TestGroup(name="Group 02", description="Temp Description")]


# Create a workspace and add users to it
async def test_prepare_workspace(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Register first account")
    # Register new account who will create the workspace
    active_user = await test_1_accounts.test_register(client_test, accounts[0])
    colored_dbg.test_success("Registered account {} {} ({})".format(
        active_user.first_name, active_user.last_name, active_user.email))
    await test_1_accounts.test_login(client_test, active_user)  # Login the active_user
    colored_dbg.test_success("Signed in under {} {} ({})".format(
        active_user.first_name, active_user.last_name, active_user.email))

    colored_dbg.test_info("Creating a workspace")
    response = await client_test.post("/workspaces",
                                      json={"name": workspace.name,
                                            "description": workspace.description},
                                      headers={"Authorization": f"Bearer {accounts[0].token}"})
    workspace.id = response.json()["id"]
    colored_dbg.test_success("Created workspace {} with id {}".format(workspace.name, workspace.id))

    colored_dbg.test_info("Adding members to workspace")
    members = []  # List of member ids to add to the workspace
    students = accounts[1:10]
    for account in students:  # Skip the first account since it is the creator of the workspace
        account = await test_1_accounts.test_register(client_test, account)  # test_register returns the new account id
        members.append(account.id)
        colored_dbg.test_info("Account {} + {} ({}) has registered".format(
            account.first_name, account.last_name, account.email))

    # Post the rest of the members to the workspace
    response = await client_test.post(f"/workspaces/{workspace.id}/members", json={"accounts": members},
                                      headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    for i in response["members"]:
        assert i["id"] in members
        members.remove(i["id"])
    assert members == []


async def test_create_group(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Create a group [POST /groups]")
    group = groups[0]
    active_user = accounts[0]

    # Get list of groups
    colored_dbg.test_info("Making sure workspace has no groups")
    response = await client_test.get(f"/workspaces/{workspace.id}/groups",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["groups"] == []
    colored_dbg.test_success("The workspace has no groups")

    # Create the groups
    for group in groups:
        response = await client_test.post(f"/workspaces/{workspace.id}/groups",
                                          json={"name": group.name, "description": group.description},
                                          headers={"Authorization": f"Bearer {active_user.token}"})
        assert response.status_code == status.HTTP_201_CREATED
        response = response.json()
        assert response["name"] == group.name
        group.id = response["id"]  # Set the group id
        colored_dbg.test_success("Created group {} with id {}".format(group.name, group.id))


async def test_create_group_duplicate_name(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Create a group with duplicate name [POST /groups]")
    group = groups[0]
    active_user = accounts[0]

    # Create a group with duplicate name
    response = await client_test.post(f"/workspaces/{workspace.id}/groups",
                                      json={"name": group.name, "description": group.description},
                                      headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    colored_dbg.test_success("Group with duplicate name cannot be created")


async def test_get_groups(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Get list of groups [GET /groups]")
    active_user = accounts[0]

    # Find group in user's list of groups
    response = await client_test.get(f"/workspaces/{workspace.id}/groups",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()

    # Get the first group(should be the only group)
    assert len(response["groups"]) == 2
    for ws in response["groups"]:
        if ws["id"] == groups[0].id:
            assert groups[0].name == ws["name"]
            assert groups[0].description == ws["description"]
        elif ws["id"] == groups[1].id:
            assert groups[1].name == ws["name"]
            assert groups[1].description == ws["description"]
        else:
            assert False
    colored_dbg.test_success("Account has 2 groups with correct information")


async def test_get_group_wrong_id(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Get group with wrong id")
    random_id = ResourceID()
    active_user = accounts[0]

    # Get group with wrong id
    response = await client_test.get(f"/groups/{random_id}",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    colored_dbg.test_success(f"Group with id {random_id} does not exist")


async def test_get_group_info(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Get group info [GET /groups/{group_id}]")
    group = groups[0]
    active_user = accounts[0]

    # Get the group basic info and and validate basic information
    response = await client_test.get(f"/groups/{group.id}",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["name"] == group.name
    assert response["description"] == group.description
    colored_dbg.test_success("Group \"{}\" has correct name and description".format(group.name))

    # Get group members and validate that the active user is the only member
    response = await client_test.get(f"/groups/{group.id}/members",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 1
    temp = response["members"][0]
    assert temp["id"] == active_user.id
    assert temp["email"] == active_user.email
    assert temp["first_name"] == active_user.first_name
    assert temp["last_name"] == active_user.last_name
    colored_dbg.test_success(f"Group \"{group.name}\" has one member: {active_user.email}")


async def test_update_group_info(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Update group info [PATCH /groups/{group.id}]")
    group = groups[1]
    active_user = accounts[0]

    # Update the group info
    group.name = "Students"
    group.description = "Students of the course"
    response = await client_test.patch(f"/groups/{group.id}",
                                       json={"name": group.name, "description": group.description},
                                       headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["name"] == group.name
    assert response["description"] == group.description
    colored_dbg.test_success(f"Group {group.name} has updated name and description")


async def test_update_group_info_duplicate_name(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Update group info with duplicate name [PATCH /groups/{group.id}]")
    group = groups[1]
    active_user = accounts[0]

    # Update the group info
    response = await client_test.patch(f"/groups/{group.id}",
                                       json={"name": groups[0].name, "description": groups[0].description},
                                       headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    colored_dbg.test_success(f"Group {group.name} cannot be updated with duplicate name")


async def test_add_members_to_group(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Add members to group [POST /groups/{group.id}/members]")
    group = groups[0]
    active_user = accounts[0]

    members = []  # List of member ids to add to the group
    students = accounts[1:10]
    for account in students:  # Skip the first account since it is the creator of the group
        members.append(account.id)

    # Post the members to the group
    response = await client_test.post(f"/groups/{group.id}/members", json={"accounts": members},
                                      headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    for i in response["members"]:
        assert i["id"] in members
        members.remove(i["id"])
    assert members == []

    colored_dbg.test_success("All members have been successfully added to the group")


async def test_get_group_members(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Getting members of group [GET /groups/{group.id}/members]]")
    group = groups[0]
    active_user = accounts[0]

    # Check that all users were added to the group as members
    response = await client_test.get(f"/groups/{group.id}/members",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 10  # 10 accounts were added to the group
    for acc in accounts[:10]:
        assert acc.dict(include={"id", "email", "first_name", "last_name"}) in response["members"]

    colored_dbg.test_success("The group returned the correct list of members")


async def test_get_policy(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Getting list of member permissions in group [GET /groups/{group.id}/policy]")
    group = groups[0]
    active_user = accounts[0]

    # Check permission of the user who created the group
    response = await client_test.get(f"/groups/{group.id}/policy",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    # Creator of the group should have all permissions
    assert response["permissions"] == Permissions.GROUP_ALL_PERMISSIONS.name.split("|")  # type: ignore

    # Check permission of the rest of the members
    students = accounts[1:10]
    for account in students:
        response = await client_test.get(f"/groups/{group.id}/policy",
                                         params={"account_id": account.id},  # type: ignore
                                         headers={"Authorization": f"Bearer {active_user.token}"})
        response = response.json()
        assert response["permissions"] == Permissions.GROUP_BASIC_PERMISSIONS.name.split("|")  # type: ignore
    colored_dbg.test_success("All members have the correct permissions")


async def test_get_all_policies(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Getting all policies [GET /groups/{group.id}/policies]")
    group = groups[0]
    active_user = accounts[0]

    # Check permission of the user who created the group
    response = await client_test.get(f"/groups/{group.id}/policies",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["policies"]) == 10  # 10 accounts were added to the group
    temp_acc_list = [acc.dict(include={"id", "email", "first_name", "last_name"}) for acc in accounts]
    for policy in response["policies"]:
        assert policy["policy_holder"] in temp_acc_list
        if policy["policy_holder"]["id"] == accounts[0].id:
            assert policy["permissions"] == Permissions.GROUP_ALL_PERMISSIONS.name.split("|")
        else:
            assert policy["permissions"] == Permissions.GROUP_BASIC_PERMISSIONS.name.split("|")
    colored_dbg.test_success("The group returned the correct list of policies")


async def test_permissions(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Actions and permissions")
    group = groups[0]
    active_user = accounts[1]
    await test_1_accounts.test_login(client_test, active_user)  # Login the active_user

    # Try to get group info
    headers = {"Authorization": f"Bearer {active_user.token}"}
    res = await client_test.get(f"/groups/{group.id}", headers=headers)
    assert res.status_code == status.HTTP_200_OK
    res = res.json()
    assert res["name"] == group.name
    assert res["description"] == group.description
    colored_dbg.test_success("User #1 can get group info")

    # Try to update group info
    res = await client_test.patch(f"/groups/{group.id}",
                                  json={"name": "New name", "description": "New description"},
                                  headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to delete group
    res = await client_test.delete(f"/groups/{group.id}", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to get group members
    res = await client_test.get(f"/groups/{group.id}/members", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to add members to group
    res = await client_test.post(f"/groups/{group.id}/members",
                                 json={"accounts": [accounts[2].id]},
                                 headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # # Try to get group list
    # res = await client_test.get(f"/groups/{group.id}/groups", headers=headers)
    # assert res.status_code == status.HTTP_403_FORBIDDEN

    # # Try to create group
    # res = await client_test.post(f"/groups/{group.id}/groups",
    #                              json={"name": "New group", "description": "New description"},
    #                              headers=headers)
    # assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to delete members from group
    res = await client_test.delete(f"/groups/{group.id}/members/{accounts[2].id}",
                                   headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to get group permissions
    res = await client_test.get(f"/groups/{group.id}/policy", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to set group permissions
    res = await client_test.put(f"/groups/{group.id}/policy",
                                json={"permissions": Permissions.GROUP_BASIC_PERMISSIONS.name.split("|")},
                                headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # TODO: Check if any actions were missed

    colored_dbg.test_success("User #1 can't do any actions without permissions")


async def test_set_permissions(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Setting permissions of group members [PUT /groups/{group.id}/policy]")
    active_user = accounts[0]
    group = groups[0]

    # Update policy of another member
    response = await client_test.put(f"/groups/{group.id}/policy?",
                                     json={"account_id": accounts[1].id,
                                           "permissions": Permissions.GROUP_ALL_PERMISSIONS.name.split("|")},
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["permissions"] == Permissions.GROUP_ALL_PERMISSIONS.name.split("|")

    # Check permissions
    response = await client_test.get(f"/groups/{group.id}/policy?account_id={accounts[1].id}",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["permissions"] == Permissions.GROUP_ALL_PERMISSIONS.name.split("|")

    # Now the member should be able to get their policy information
    await test_1_accounts.test_login(client_test, accounts[1])  # Login the active_user
    colored_dbg.test_success("Signed in under {} {} ({})".format(
        accounts[1].first_name, accounts[1].last_name, accounts[1].email))
    response = await client_test.get(f"/groups/{group.id}/policy",
                                     headers={"Authorization": f"Bearer {accounts[1].token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["permissions"] == Permissions.GROUP_ALL_PERMISSIONS.name.split("|")

    colored_dbg.test_success("All members have the correct permissions")


# Attempt to remove a member from non existing group
async def test_delete_non_existing_group(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Testing group deletion from non existing group")
    active_user = accounts[0]

    random_group_id = ResourceID()

    response = await client_test.delete(f"/groups/{random_group_id}",
                                        headers={"Authorization": f"Bearer {active_user.token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Delete the groups
async def test_delete_group(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Testing group deletion")
    active_user = accounts[0]
    headers = {"Authorization": f"Bearer {active_user.token}"}

    for group in groups:
        # Get the group
        colored_dbg.test_info("Searching for group")
        response = await client_test.get(f"/groups/{group.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        response = response.json()
        assert response["name"] == group.name
        colored_dbg.test_success(f'Group "{group.name}" found')

        # Delete the group
        colored_dbg.test_info(f'Deleting group "{group.name}"')
        response = await client_test.delete(f"/groups/{group.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Test to get the group
        response = await client_test.get(f"/groups/{group.id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        colored_dbg.test_success(f'Group "{group.name}" has been successfully deleted')

    # Delete the workspace
    response = await client_test.delete(f"/workspaces/{workspace.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    colored_dbg.test_info(f'Deleting workspace "{workspace.name}"')

    # TODO: Check that no users have the group in their groups list


# Delete accounts
async def test_cleanup(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Cleaning up")
    await Account.find(In(Account.id, [ResourceID(account.id) for account in accounts])).delete()
    colored_dbg.test_success("All users deleted")
