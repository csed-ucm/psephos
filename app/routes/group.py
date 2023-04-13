# FastAPI
from fastapi import APIRouter, Depends
from app.actions import group as GroupActions
from app.schemas import group as GroupSchemas
from app.models.group import Group
from app.exceptions import group as GroupExceptions

# APIRouter creates path operations for user module
router = APIRouter()


# Dependency to get a group by id and verify it exists
async def get_group(group_id: GroupSchemas.GroupID) -> Group:
    """
    Returns a group with the given id.
    """
    workspace = await Group.get(group_id)
    if not workspace:
        raise GroupExceptions.GroupNotFound(group_id)
    return workspace


# Get all groups
@router.get("/", response_description="Get all groups")
async def get_all_groups() -> GroupSchemas.GroupList:
    return await GroupActions.get_all_groups()


# Get group info by id
@router.get("/{group_id}", response_description="Get a group")
async def get_group_info(group: Group = Depends(get_group)) -> GroupSchemas.GroupReadFull:
    return await GroupActions.get_group(group)


# Update group info
@router.patch("/{group_id}", response_description="Update a group")
async def update_group(group_data: GroupSchemas.GroupUpdateIn,
                       group: Group = Depends(get_group)) -> GroupSchemas.GroupReadShort:
    return await GroupActions.update_group(group, group_data)


# Delete a group
@router.delete("/{group_id}", response_description="Delete a group")
async def delete_group(group: Group = Depends(get_group)):
    return await GroupActions.delete_group(group)


# Get a list of group members
@router.get("/{group_id}/members", response_description="Get a list of group members")
async def get_group_members(group: Group = Depends(get_group)):
    return await GroupActions.get_members(group)


# Add member to group
@router.post("/{group_id}/members", response_description="Get a group")
async def add_member(member_data: GroupSchemas.AddMembers, group: Group = Depends(get_group)):
    return await GroupActions.add_members(group, member_data)
