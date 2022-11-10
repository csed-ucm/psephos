from distutils.dep_util import newer_group
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from typing import List
from app.mongo_db import mainDB as Database
from app.models.group import Group
from app.models.user import User as userModel 
from app.models.user_manager import auth_backend, current_active_user, fastapi_users
from beanie.operators import In
from beanie import PydanticObjectId

#APIRouter creates path operations for user module
router = APIRouter(
    prefix="/group",
    tags=["Groups"],
    responses={404: {"description": "Not found"}},
)

# TODO: Add api callbaks for group creation, deletion, and modification
# TODO: Add api callbaks for group membership management: add, remove, change role

# List all groups that a user is a member of
# TODO: Add response model
@router.get("/", response_description="List all groups")  # response_model=List[Group]
async def list_groups(owner_only: bool, user: userModel = Depends(current_active_user)):
    groups = await Group.find(In(Group.id, user.groups)).to_list()
    
    owner_groups = []
    admin_groups = []
    user_groups = []
    
    use_id = user.id
    for group in groups:
        if use_id == group.owner:
            owner_groups.append(group.name)
        if use_id in group.admins:
            admin_groups.append(group.name)
        if use_id in group.users:
            user_groups.append(group.name)
        # groups = await Group.find({"$or": [{"owner": user_id}, {"users": user.id}, {"admins": user.id}]}).to_list()
    return {"owner_groups": owner_groups, "admin_groups": admin_groups, "user_groups": user_groups}


# Create a new group with user as the owner
@router.post("/", response_description="Create new group", response_model=Group)
async def create_group(name: str, user: userModel = Depends(current_active_user)):
    # Todo: Check if group name is unique
    # if (await Group.find({"name": name})):
    #     return 400


    # Add groupto user's groups list
    new_group = await Group(name=name, owner=user.id, admins=[user.id], users=[user.id]).insert()
    user.groups.append(new_group.id)
    # created_group = await Group.get(new_group.id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(new_group))

# @router.get("/{id}", response_description="Get a single group", response_model=groupModel)
# async def show_group(id: str):
#     if (group := await Database["groups"].find_one({"_id": id})) is not None:
#         return group

#     raise HTTPException(status_code=404, detail=f"group {id} not found")


# @router.put("/{id}", response_description="Update a group", response_model=groupModel)
# async def update_group(id: str, group: groupModel = Body(...)):
#     new_group = {k: v for k, v in group.dict().items() if v is not None}

#     if len(new_group) >= 1:
#         update_result = await Database["groups"].update_one({"_id": id}, {"$set": group})

#         if update_result.modified_count == 1:
#             if (
#                 updated_group := await Database["groups"].find_one({"_id": id})
#             ) is not None:
#                 return updated_group

#     if (existing_group := await Database["groups"].find_one({"_id": id})) is not None:
#         return existing_group

#     raise HTTPException(status_code=404, detail=f"group {id} not found")


# @router.delete("/{id}", response_description="Delete a group")
# async def delete_group(id: str):
#     delete_result = await Database["groups"].delete_one({"_id": id})

#     if delete_result.deleted_count == 1:
#         return Response(status_code=status.HTTP_204_NO_CONTENT)

#     raise HTTPException(status_code=404, detail=f"group {id} not found")

# Add a user to a group
@router.post("/{group_id}/add_user", response_description="Add a user to a group")
async def add_user_to_group(group_id: PydanticObjectId, email: str, user: userModel = Depends(current_active_user)):
    # Check if user is an admin of the group
    if (group := await Group.get(group_id)) is not None:
        if user.id not in group.admins:
            raise HTTPException(status_code=403, detail="User is not an admin of the group")
        pass
    else:
        raise HTTPException(status_code=404, detail=f"group {group_id} not found")

    # Check if user exists
    if (new_user := await userModel.find_one({"email": email})) is not None:
        # Check if user is already in the group
        if new_user.id in group.users:
            raise HTTPException(status_code=400, detail="User is already in the group")
        else:
            group.users.append(new_user.id)
            new_user.groups.append(group.id)
            await group.save()
            await new_user.save()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=404, detail=f"user {email} not found")