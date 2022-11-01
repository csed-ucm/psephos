from distutils.dep_util import newer_group
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from typing import List
from app.mongo_db import mainDB as Database
from app.models.group import Group
from app.models.user import User as userModel 
from app.models.user_manager import auth_backend, current_active_user, fastapi_users


#APIRouter creates path operations for user module
router = APIRouter(
    prefix="/group",
    tags=["Groups"],
    responses={404: {"description": "Not found"}},
)


# List all groups that a user is a member of
@router.get("/", response_description="List all groups", response_model=List[Group])
async def list_groups(owner_only: bool, user: userModel = Depends(current_active_user)):
    user_id = user.id
    if owner_only:
        groups = await Group.find({"owner": user_id}).to_list()
        # groups = await Group.find(Group.owner == user_id).to_list()
    else:
        groups = await Group.find({"$or": [{"owner": user_id}, {"users": user.id}, {"admins": user.id}]}).to_list()
    return groups


# Create a new group with user as the owner
@router.post("/", response_description="Create new group", response_model=Group)
async def create_group(name: str, user: userModel = Depends(current_active_user)):
    new_group = await Group(name=name, owner=user.id, admins=[user.id], users=[user.id]).insert()
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