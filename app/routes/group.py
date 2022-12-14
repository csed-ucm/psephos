# FastAPI
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from fastapi.logger import logger
# pydantic
from pydantic import Field, EmailStr
# Types
from typing import List
# Beanie
from beanie import PydanticObjectId
from beanie.operators import In, Push
# Local imports
from app.mongo_db import mainDB as Database
from app.models.group import Group
from app.models.user import User
from app.models.user_manager import auth_backend, current_active_user, fastapi_users
from app.exceptions import group as group_exceptions
from app.exceptions import user as user_exceptions
from app.schemas.group import *
from app.schemas.user import *


#APIRouter creates path operations for user module
router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
    responses={404: {"description": "Not found"}},
)


# TODO: Add api callbacks for group creation, deletion, and modification
# TODO: Add api callbacks for group membership management: add, remove, change role


current_superuser = fastapi_users.current_user(active=True, superuser=True)


# List all groups can be used later for search queries
@router.get("/", response_description="List all groups")  # response_model=List[Group]
async def list_groups(user: User = Depends(current_active_user), 
                      group_name: str | None = None, 
                      member_data: PydanticObjectId | str | None = None):
    query = []
    if group_name:
        query.append({"name": group_name})
    if member_data:
        member = None
        if member_data.__class__ == str:
            member = await User.find_one({"email": member_data})
        elif member_data.__class__ == PydanticObjectId:
            member = await User.find_one({"_id": member_data})
        
        if member:
            member_id = member.id
        else:
            raise user_exceptions.UserNotFound(member_data)
            
        query.append({"owner": member_id})
        # TODO: Add member search for other roles
    # NOTE: Users can only see groups they are a member of
    # NOTE: Superusers can see all groups
    if user.is_superuser == False:
        query.append({"members": user.id})
         
    search = {"$and": query} if query else {}
    all_groups = await Group.find(search).to_list()
    # search_result = []
    
    # for group in all_groups:
    #     search_result.append(group)

    # return search_result
    return all_groups


# Create a new group with user as the owner
@router.post("/", response_description="Create new group", response_model=GroupCreateOut)
async def create_group(group: GroupCreateIn = Body(...),
                       user: User = Depends(current_active_user)):
    # Todo: Check if group name is unique
    # if (await Group.find({"name": name})):
    #     return 400

    # NOTE: The update method is not working for some reason
    # await User.update({"_id": user.id}, {"$push": {"groups": new_group.id}})

    # HACK: Thus, find, update, and save user manually instead
    creator = await User.get(user.id)
    if creator:
        # Add group to user's groups list
        new_group = await Group(name=group.name, description=group.description, owner=user.id, admins=[user.id], members=[user.id]).insert()
        # if not new_group:
        #     raise group_exceptions.GroupCreationError(group.name)
        creator.groups.append(new_group.id)
        await creator.save()
    else:
        raise user_exceptions.UserNotFound(user.id)
    created_group = await Group.get(new_group.id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(created_group))


# Get group by id
@router.get("/{group_id}", response_description="Get group by id", response_model=GroupRead)
async def get_group(group_id: PydanticObjectId, user: User = Depends(current_active_user)):
    # find group by id
    group = await Group.get(group_id)
    if group:
        if group.owner == user.id or user.id in group.admins or user.id in group.members:
            owner = await User.get(group.owner)
            if owner:
                email = owner.email
                name = "{} {}".format(owner.first_name, owner.last_name)
                return GroupRead(name=group.name, description=group.description, owner_name=name, owner_email=email)
        else:
            raise group_exceptions.UserNotAuthorized(user, group, "access in")
    else:
        raise group_exceptions.GroupNotFound(group_id)
    

# Delete a group
@router.delete("/{group_id}", response_description="Delete group")
async def delete_group(group_id: PydanticObjectId, user: User = Depends(current_active_user)):
    # Check if user is owner of group
    
    group = await Group.get(group_id)
    
    if group is None:
        raise group_exceptions.GroupNotFound(group_id)
    
    if group.owner != user.id:
        raise group_exceptions.UserNotAuthorized(user, group)
    # Remove group from user's groups list
    user.groups.remove(group_id)
    # Remove group from database
    await group.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update a group
@router.put("/{id}", response_description="Update a group", response_class=GroupUpdateOut)
async def update_group(id: str, group: GroupUpdateIn = Body(...)):
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


# Get the owner of a group
@router.get("/{group_id}/owner", response_description="Get group owner", response_model=UserReadBasicInfo)
async def get_group_owner(group_id: PydanticObjectId, user: User = Depends(current_active_user)):
    
    group = await Group.get(group_id)
    if group:
        if user.id not in group.members and user.is_superuser == False:
            raise group_exceptions.UserNotAuthorized(user, group, "access in")
        
        owner = await User.get(group.owner)
        if not owner:
            # This should never happen
            raise user_exceptions.UserNotFound(group.owner)
        return owner
    else:
        raise group_exceptions.GroupNotFound(group_id)


# Get group admins
@router.get("/{group_id}/admins/", response_description="Get list of group administrators", response_model=GroupReadMembers)
async def get_group_admins(group_id: PydanticObjectId, user: User = Depends(current_active_user)):
    group = await Group.get(group_id)
    admins = []
    if group:
        if user.id not in group.members and user.is_superuser == False:
            raise group_exceptions.UserNotAuthorized(user, group, "access in")
        admins = await User.find({"_id": {"$in": group.admins}}).to_list()
    else:
        raise group_exceptions.GroupNotFound(group_id)
    # Return list of admins or empty list
    return GroupReadMembers(members=admins)


# Get members of a group
@router.get("/{group_id}/members", response_description="Get group members", response_model=GroupReadMembers)
async def get_group_members(group_id: PydanticObjectId, user: User = Depends(current_active_user)):
    group = await Group.get(group_id)
    members = []
    if group:
        if user.id not in group.members and user.is_superuser == False:
            raise group_exceptions.UserNotAuthorized(user, group, "access in")
        filter = [_user for _user in group.members if _user not in group.admins]
        members = await User.find({"_id": {"$in": filter}}).to_list()
    else:
        raise group_exceptions.GroupNotFound(group_id)
    return GroupReadMembers(members=members)

# Add user to group
@router.post("/{group_id}/members", response_description="Add user(s) to a group")
async def add_user_to_group(group_id: PydanticObjectId, InputModel: GroupAddMembers, user: User = Depends(current_active_user)):
    """
    Add member(s) to a group. The front-end application must do validation to ensure 
    that the user exists in the database and is not already a member of the group.
    This function also does the same validation checks; However, no users will be added 
    if any error occurs.
    
    The function takes a list of JSON objects(Models) with email of the new user and the 
    role(privilege level) in the group.
    
    Possible outcomes:
     - The function will return a list of emails of users that were not found in the database.
     - The function will return an error if a user is already a member of the group
     - The function will successfully add the users to the group
    
    """
    
    # TODO: Check if only one email is provided

    
    
    # Check if user is an admin of the group
    if (group := await Group.get(group_id)) is not None:
        if user.id not in group.admins:
            raise group_exceptions.UserNotAuthorized(user, group)
    else:
        raise group_exceptions.GroupNotFound(group_id)
    
    # Copy emails to a dictionary
    email_dict = {}
    for member in InputModel.members:
        email_dict[member.email] = member.role
    
    # Get the users from the database
    new_members = {}
    email_list = list(email_dict.keys())
    async for user in User.find({"email": {"$in": email_list}}):
        if user:
            email_list.remove(user.email)
            new_members[user.id] = user
     
    # Check if all emails are valid
    if email_list:
        raise HTTPException(status_code=404, detail=f"Users with emails {email_list} not found")

    # Check if users are already in the group
    for _, (i, new_user) in enumerate(new_members.items()): 
        if new_user.id in group.members:
            raise group_exceptions.UserAlreadyExists(new_user, group)
    
    await group.update({"$push": {"members": {"$each": list(new_members.keys())}}})
    await User.find({"_id": {"$in": list(new_members.keys())}}).update({"$push": {"groups": group_id}}) 
    
        
# Remove a user from a group
@router.delete("/{group_id}/member/{email}", response_description="Remove a user from a group")
async def remove_user(group_id: PydanticObjectId, email: str, user: User = Depends(current_active_user)):
    # Check if user is an admin of the group
    if (group := await Group.get(group_id)) is not None:
        # Check if user is an admin of the group
        if user.id not in group.admins:
            raise group_exceptions.UserNotAuthorized(user, group, "remove users from")
        # Prohibit the user from removing themselves
        if user.email == email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove yourself from the group")
        # Prohibit the user from removing the owner of the group
        if group.owner == user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove the owner of the group")
        # Check if user exists
        if (deleted_user := await User.find_one({"email": email})) is not None:
            # Check if user is in the group
            if deleted_user.id not in group.members:
                raise group_exceptions.UserNotInGroup(deleted_user, group)
            else:
                # Remove user from group and group from user
                await User.update({"_id": deleted_user.id}, {"$pull": {"groups": group_id}})
                await Group.update({"_id": group_id}, {"$pull": {"members": deleted_user.id, "admins": deleted_user.id}})
                # Check that the user has been removed from the group
                if (group := await Group.get(group_id)) is not None:
                    if deleted_user.id in group.members or deleted_user.id in group.admins:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                            detail="User was not removed from the group")
                return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise group_exceptions.GroupNotFound(group_id)