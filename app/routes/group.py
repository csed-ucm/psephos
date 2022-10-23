from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from typing import List
from app.mongo_db import Groups_DB as Database
from app.models.group import Group as groupModel 


#APIRouter creates path operations for user module
router = APIRouter(
    prefix="/group",
    tags=["Groups"],
    responses={404: {"description": "Not found"}},
)

# Create a new group with user as the owner
# TODO: Add Uses dependency
# Use user info to set owner
@router.post("/", response_description="Create new group", response_model=groupModel)
async def create_group(group: groupModel = Body(...)):
    new_group = jsonable_encoder(group)
    new_group = await Database.insert_one(new_group)
    created_group = await Database["groups"].find_one({"_id": new_group.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_group)

# List all groups that a user is a member of
@router.get("/", response_description="List all groups", response_model=List[groupModel])
async def list_groups():
    # Motor's to_list method requires a max document count argument. 
    # For this example, I have hardcoded it to 1000; 
    groups = await Database["groups"].find().to_list(1000)
    return groups


@router.get("/{id}", response_description="Get a single group", response_model=groupModel)
async def show_group(id: str):
    if (group := await Database["groups"].find_one({"_id": id})) is not None:
        return group

    raise HTTPException(status_code=404, detail=f"group {id} not found")


@router.put("/{id}", response_description="Update a group", response_model=groupModel)
async def update_group(id: str, group: groupModel = Body(...)):
    new_group = {k: v for k, v in group.dict().items() if v is not None}

    if len(new_group) >= 1:
        update_result = await Database["groups"].update_one({"_id": id}, {"$set": group})

        if update_result.modified_count == 1:
            if (
                updated_group := await Database["groups"].find_one({"_id": id})
            ) is not None:
                return updated_group

    if (existing_group := await Database["groups"].find_one({"_id": id})) is not None:
        return existing_group

    raise HTTPException(status_code=404, detail=f"group {id} not found")


@router.delete("/{id}", response_description="Delete a group")
async def delete_group(id: str):
    delete_result = await Database["groups"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"group {id} not found")