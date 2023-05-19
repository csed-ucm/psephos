from faker import Faker
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from pydantic import BaseModel
from httpx import AsyncClient
from app.app import app
from app.utils import colored_dbg
from app.models.documents import ResourceID, Account
from app.schemas import workspace as WorkspaceSchema
from tests import test_1_accounts
from app.utils import permissions as Permissions


fake = Faker()
client = TestClient(app)

# TODO: Add settings for testing, i.e. testing database
# class Settings(BaseSettings):

pytestmark = pytest.mark.asyncio


@pytest.mark.skip()
def create_random_user():
    first_name = fake.first_name()
    last_name = fake.unique.last_name()
    email = (first_name[0] + last_name + "@ucmerced.edu").lower()
    password = fake.password()
    return test_1_accounts.TestAccount(first_name=first_name, last_name=last_name, email=email, password=password)


@pytest.mark.skip()
class TestWorkspace(BaseModel):
    id: ResourceID | None = None
    name: str = "Workspace " + fake.aba()
    description: str = fake.sentence()
    owner: ResourceID | None = None
    policies: list[ResourceID] = []
    members: list[ResourceID] = []


global accounts, workspace
accounts = [create_random_user() for i in range(10)]
workspace = TestWorkspace()


async def test_create_workspace(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Create a workspace [POST /workspaces]")

    # Register new account who will create the workspace
    active_user = await test_1_accounts.test_register(client_test, accounts[0])
    colored_dbg.test_success("Registered account {} {} ({})".format(
        active_user.first_name, active_user.last_name, active_user.email))
    await test_1_accounts.test_login(client_test, active_user)  # Login the active_user
    colored_dbg.test_success("Signed in under {} {} ({})".format(
        active_user.first_name, active_user.last_name, active_user.email))

    # Get list of workspaces
    response = await client_test.get("/workspaces", headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["workspaces"] == []
    colored_dbg.test_success("Account has no workspaces")

    # Create a workspace
    response = await client_test.post("/workspaces",
                                      json={"name": workspace.name, "description": workspace.description},
                                      headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_201_CREATED
    response = response.json()
    assert response["name"] == workspace.name
    workspace.id = response["id"]  # Set the workspace id
    colored_dbg.test_success("Created workspace {} with id {}".format(workspace.name, workspace.id))


async def test_create_workspace_duplicate_name(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Create a workspace with duplicate name [POST /workspaces]")
    active_user = accounts[0]

    # Create a workspace with duplicate name
    response = await client_test.post("/workspaces",
                                      json={"name": workspace.name, "description": workspace.description},
                                      headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    colored_dbg.test_success("Workspace with duplicate name cannot be created")


async def test_get_workspaces(client_test: AsyncClient):
    print("\n")
    active_user = accounts[0]
    colored_dbg.test_info("Get list of workspaces [GET /workspaces]")

    # Find workspace in user's list of workspaces
    response = await client_test.get("/workspaces",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()

    # Get the first workspace(should be the only workspace)
    assert len(response["workspaces"]) == 1
    response = response["workspaces"][0]
    assert response["id"] == workspace.id
    assert response["name"] == workspace.name
    assert response["description"] == workspace.description
    colored_dbg.test_success("Account has 1 workspace \"{}\" with id {}".format(workspace.name, workspace.id))


async def test_get_workspace_wrong_id(client_test: AsyncClient):
    print("\n")
    random_id = ResourceID()
    colored_dbg.test_info(f"Get workspace with wrong id [GET /workspaces/{random_id}]")
    active_user = accounts[0]

    # Get workspace with wrong id
    response = await client_test.get(f"/workspaces/{random_id}",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    colored_dbg.test_success(f"Workspace with id {random_id} does not exist")


async def test_get_workspace_info(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info(f"Get workspace info [GET /workspace/{workspace.id}] ")
    active_user = accounts[0]

    # Get the workspace basic info and and validate basic information
    response = await client_test.get(f"/workspaces/{workspace.id}",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["name"] == workspace.name
    assert response["description"] == workspace.description
    colored_dbg.test_success("Workspace \"{}\" has correct name and description".format(workspace.name))

    # Get workspace members and validate that the active user is the only member
    response = await client_test.get(f"/workspaces/{workspace.id}/members",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == 1
    temp = response["members"][0]
    assert temp["id"] == active_user.id
    assert temp["email"] == active_user.email
    assert temp["first_name"] == active_user.first_name
    assert temp["last_name"] == active_user.last_name
    colored_dbg.test_success(f"Workspace \"{workspace.name}\" has one member: {active_user.email}")


async def test_add_members_to_workspace(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info(f"Add members to workspace \"{workspace.name}\"")
    active_user = accounts[0]

    members = []  # List of member ids to add to the workspace
    for account in accounts[1:]:  # Skip the first account since it is the creator of the workspace
        account = await test_1_accounts.test_register(client_test, account)  # test_register returns the new account id
        members.append(account.id)
        colored_dbg.test_info("Account {} + {} ({}) has registered".format(
            account.first_name, account.last_name, account.email))

    # Post the members to the workspace
    response = await client_test.post(f"/workspaces/{workspace.id}/members", json={"accounts": members},
                                      headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    for i in response["members"]:
        assert i["id"] in members
        members.remove(i["id"])
    assert members == []

    colored_dbg.test_success("All members have been successfully added to the workspace")


async def test_get_workspace_members(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info(f"Getting members of workspace \"{workspace.name}\"")
    active_user = accounts[0]

    # Check that all users were added to the workspace as members
    response = await client_test.get(f"/workspaces/{workspace.id}/members",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert len(response["members"]) == len(accounts)
    for acc in accounts:
        assert acc.dict(include={"id", "email", "first_name", "last_name"}) in response["members"]

    colored_dbg.test_success("The workspace returned the correct list of members")


async def test_add_group(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info(f"Adding group to workspace \"{workspace.name}\"")
    active_user = accounts[0]

    # Create a group
    group = await test_2_groups.test_create_group(client_test, GroupCreate(name="test_group"))

    # Add the group to the workspace
    response = await client_test.post(f"/workspaces/{workspace.id}/groups", json={"groups": [group.id]},
                                      headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert response["groups"][0]["id"] == group.id
    colored_dbg.test_success(f"Group \"{group.name}\" has been added to the workspace")


async def test_get_permissions(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info(f"Getting list of member permissions in workspace \"{workspace.name}\"")
    active_user = accounts[0]

    # Check permission of the user who created the workspace
    response = await client_test.get(f"/workspaces/{workspace.id}/policy",
                                     headers={"Authorization": f"Bearer {active_user.token}"})
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    # Creator of the workspace should have all permissions
    assert response["permissions"] == Permissions.WORKSPACE_ALL_PERMISSIONS.name.split("|")  # type: ignore

    # Check permission of the rest of the members
    for i in range(1, len(accounts)):
        response = await client_test.get(f"/workspaces/{workspace.id}/policy",
                                         params={"account_id": accounts[i].id},  # type: ignore
                                         headers={"Authorization": f"Bearer {active_user.token}"})
        response = response.json()
        assert response["permissions"] == Permissions.WORKSPACE_BASIC_PERMISSIONS.name.split("|")  # type: ignore
    colored_dbg.test_success("All members have the correct permissions")


async def test_permissions(client_test: AsyncClient):
    print("\n")
    colored_dbg.test_info("Try actions without permissions")
    active_user = accounts[1]
    await test_1_accounts.test_login(client_test, active_user)  # Login the active_user

    # Try to get workspace info
    headers = {"Authorization": f"Bearer {active_user.token}"}
    res = await client_test.get(f"/workspaces/{workspace.id}", headers=headers)
    assert res.status_code == status.HTTP_200_OK
    res = res.json()
    assert res["name"] == workspace.name
    assert res["description"] == workspace.description
    colored_dbg.test_success("User #1 can get workspace info")

    # Try to update workspace info
    res = await client_test.patch(f"/workspaces/{workspace.id}",
                                  json={"name": "New name", "description": "New description"},
                                  headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to delete workspace
    res = await client_test.delete(f"/workspaces/{workspace.id}", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to get workspace members
    res = await client_test.get(f"/workspaces/{workspace.id}/members", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to add members to workspace
    res = await client_test.post(f"/workspaces/{workspace.id}/members",
                                 json={"accounts": [accounts[2].id]},
                                 headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to get group list
    res = await client_test.get(f"/workspaces/{workspace.id}/groups", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to create group
    res = await client_test.post(f"/workspaces/{workspace.id}/groups",
                                 json={"name": "New group", "description": "New description"},
                                 headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to delete group
    # res = await client_test.delete(f"/workspaces/{workspace.id}/groups/{groups[0].id}", headers=headers)
    # assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to delete members from workspace
    res = await client_test.delete(f"/workspaces/{workspace.id}/members/{accounts[2].id}",
                                   headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to get workspace permissions
    res = await client_test.get(f"/workspaces/{workspace.id}/policy", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # Try to set workspace permissions
    res = await client_test.put(f"/workspaces/{workspace.id}/policy",
                                json={"permissions": Permissions.WORKSPACE_BASIC_PERMISSIONS.name.split("|")},
                                headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # TODO: Check if any actions were missed

    colored_dbg.test_success("User #1 can't do any actions without permissions")

# async def test_set_permissions(client_test: AsyncClient):
#     print("\n")
#     colored_dbg.test_info(f"Setting permissions of workspace \"{workspace.name}\"")
#     active_user = accounts[0]

#     # Set permissions of the user who created the workspace
#     # response = await client_test.put(f"/workspaces/{workspace.id}/permissions",
#     #                                  json={"permissions": ["READ", "WRITE"]},
#     #                                  headers={"Authorization": f"Bearer {active_user.token}"})
#     # assert response.status_code == status.HTTP_200_OK
#     # response = response.json()
#     # assert response["permissions"] == ["READ", "WRITE"]

#     # Set permissions of the rest of the members
#     # for acc in accounts:
#     #     acc = {"id": acc.id, "email": acc.email, "first_name": acc.first_name, "last_name": acc.last_name}
#     #     assert acc in response["permissions"]

#     colored_dbg.test_success("All members have the correct permissions")


# # Attempt to delete a user from non existing workspace
# async def test_delete_workspace_no_owner(client_test: AsyncClient):
#     print("\n")
#     colored_dbg.test_info("Testing workspace deletion from non existing workspace")

#     random_workspace_id = ResourceID()

#     # Delete the workspace
#     # NOTE: pytest.raises() does not work(with async functions?)
#     # with pytest.raises(WorkspaceNotFound):
#     #     response = await client_test.delete(f"/workspaces/{random_workspace_id}",
#     #                                         headers={"Authorization": f"Bearer {owner.token}"})
#     #     print(response.json())
#     response = await client_test.delete(f"/workspaces/{random_workspace_id}",
#                                         headers={"Authorization": f"Bearer {owner.token}"})
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.json()["detail"] == f'Workspace with id {str(random_workspace_id)} not found'

#     colored_dbg.test_success("Workspace deletion from non existing workspace failed as expected")
#     # assert response.status_code == status.HTTP_404_NOT_FOUND
#     # assert


# # Delete the workspace and users
# async def test_delete_workspace(client_test: AsyncClient):
#     print("\n")
#     colored_dbg.test_info("Testing workspace deletion")
#     # Get the workspace
#     response = await client_test.get(f"/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {owner.token}"})
#     assert response.status_code == status.HTTP_200_OK
#     response = response.json()
#     assert response["name"] == workspace.name
#     colored_dbg.test_info(f'Workspace "{workspace.name}" exists')

#     # Delete the workspace
#     response = await client_test.delete(f"/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {owner.token}"})
#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     colored_dbg.test_info(f'Workspace "{workspace.name}" has been successfully deleted')

#     # Test to get the workspace
#     response = await client_test.get(f"/workspaces/{workspace.id}", headers={"Authorization": f"Bearer {owner.token}"})
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     colored_dbg.test_info(f'Workspace "{workspace.name}" is not found')

#     # TODO: Check that no users have the workspace in their workspaces list

#     # Delete the users by email
#     await Account.find({"email": {"$in": [user.email for user in (users+admins+[owner])]}}).delete()
#     colored_dbg.test_info("All users deleted")
