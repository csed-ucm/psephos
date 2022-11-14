# FastAPI
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
# pydantic
from pydantic import Field
# Types
from typing import List
# Beanie
from beanie import PydanticObjectId
from beanie.operators import In
# Local imports
from app.mongo_db import mainDB as Database
from app.models.group import Group
from app.models.user import User
from app.models.user_manager import auth_backend, current_active_user, fastapi_users
from app.exceptions import group as group_exceptions
from app.schemas.group import GroupRead, GroupCreate

#APIRouter creates path operations for user module
router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
    responses={404: {"description": "Not found"}},
)

# TODO: Add api callbacks for group creation, deletion, and modification
# TODO: Add api callbacks for group membership management: add, remove, change role

# List all groups can be used later for search queries
# TODO: Add response model
# TODO: Add query parameters
@router.get("/", response_description="List all groups")  # response_model=List[Group]
async def list_groups(user: User = Depends(current_active_user), 
                      name: str | None = None, 
                      owner: PydanticObjectId | None = None):
    
    query = []
    if name:
        query.append({"name": name})
    if owner:
        query.append({"owner": owner})
         
    search = {"$and": query} if query else {}
    all_groups = await Group.find(search).to_list()
    search_result = []
    
    for group in all_groups:
        search_result.append(group)

    return search_result


# Create a new group with user as the owner
@router.post("/", response_description="Create new group", response_model=GroupCreate)
async def create_group(group: GroupCreate = Body(...),
                       user: User = Depends(current_active_user)):
    # Todo: Check if group name is unique
    # if (await Group.find({"name": name})):
    #     return 400

    # Add group to user's groups list
    new_group = await Group(name=group.name, owner=user.id, admins=[user.id], users=[user.id]).insert()
    user.groups.append(new_group.id)
    # created_group = await Group.get(new_group.id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(new_group))

# Get group by id
@router.get("/{group_id}", response_description="Get group by id", response_model=GroupRead)
async def get_group(group_id: PydanticObjectId, user: User = Depends(current_active_user)):
    # find group by id
    group = await Group.get(group_id)
    

# Delete a group
@router.delete("/{group_id}", response_description="Delete group")
async def delete_group(group_id: PydanticObjectId, user: User = Depends(current_active_user)):
    # Check if user is owner of group
    
    group = await Group.get(group_id)
    
    if  group is None:
        raise group_exceptions.GroupNotFound(group_id)
    
    if group.owner != user.id:
        raise group_exceptions.UserNotAuthorized(user, group)
    # Remove group from user's groups list
    user.groups.remove(group_id)
    # Remove group from database
    await group.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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


# 
@router.post("/{group_id}/users", response_description="Add a user to a group")
async def add_user_to_group(group_id: PydanticObjectId, email: str, user: User = Depends(current_active_user)):
    # Check if user is an admin of the group
    if (group := await Group.get(group_id)) is not None:
        if user.id not in group.admins:
            raise HTTPException(status_code=403, detail="User is not an admin of the group")
    else:
        raise HTTPException(status_code=404, detail=f"group {group_id} not found")

    # Check if user exists
    if (new_user := await User.find_one({"email": email})) is not None:
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
    

# Add a users to a group
@router.post("/{group_id}/users", response_description="Add a user to a group")
async def add_user(group_id: PydanticObjectId, email: str, user: User = Depends(current_active_user)):
    # Check if user is an admin of the group
    if (group := await Group.get(group_id)) is not None:
        if user.id not in group.admins:
            raise HTTPException(status_code=403, detail="User is not an admin of the group")
    else:
        raise HTTPException(status_code=404, detail=f"group {group_id} not found")

    # Check if user exists
    if (new_user := await User.find_one({"email": email})) is not None:
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

# Remove a user from a group
# @router.post("/{group_id}/remove_user", response_description="Remove a user from a group")
# async def remove_user(group_id: PydanticObjectId, email: str, user: User = Depends(current_active_user)):
#     # Check if user is an admin of the group
#     if (group := await Group.get(group_id)) is not None:
#         if user.id not in group.admins:
#             raise group_exceptions.user_not_authorized(user, group)
    
#     # Check if user exists
#     if (new_user := await User.find_one({"email": email})) is not None:
#         # Check if user is already in the group
#         if new_user.id not in group.users:
#             raise HTTPException(status_code=400, detail="User is not in the group")
#         else:
#             group.users.remove(new_user.id)
#             new_user.groups.remove(group.id)
#             await group.save()
#             await new_user.save()
#             return Response(status_code=status.HTTP_204_NO_CONTENT)