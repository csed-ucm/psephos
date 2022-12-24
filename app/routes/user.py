from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.models.user import User
from app.models.user_manager import current_active_user
from app.schemas.user import UserID
from app.schemas.group import GroupList
# from beanie import PydanticObjectId
from app.exceptions import user as user_exceptions
from app.utils.user import get_user_groups, check_user_exists
from app.utils.colored_dbg import info

# APIRouter creates path operations for user module
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


# List all groups that a user is a member of
@router.get("/groups",
            response_description="List all groups that current user is a member of",
            responses={
                   200: {"description": "List of groups.", "model": GroupList},
                   404: {"description": "User not found"},
                   })
async def list_my_groups(user: User = Depends(current_active_user)) -> GroupList:
    """
        ## Get current user groups

        This route returns all groups that currently logged in user is a member of, \
        with the user's role in that group.

    """
    if not user:
        raise user_exceptions.UserNotFound(user)
    return await get_user_groups(user)


# List all groups that a user is a member of
@router.get("/{user_id}/groups",
            response_description="List all groups of user with id {user_id}",
            responses={
                   200: {"description": "List of groups.", "model": GroupList},
                   404: {"description": "User not found"},
                   })
async def list_user_groups(user_id: UserID,
                           user: User = Depends(current_active_user)) -> GroupList:
    """
        ## Delete current user account

        This route, finds user by provided id, or raises a HTTP exception (User not found).
        If user is found, lists all groups that a user is a member of, with the user's role in that group.

        ### Request Query Parameters

        **user_id**: id of the user whose groups are to be listed
    """
    found_user = await check_user_exists(user_id)
    return await get_user_groups(found_user)


# Delete current user account
@router.delete("/me",
               status_code=status.HTTP_204_NO_CONTENT,
               response_description="The account has been deleted",
               responses={
                   204: {"description": "The account has been deleted"},
                   404: {"description": "User not found"},
                   500: {"description": "User was not deleted"}
                   })
async def delete_user(user: User = Depends(current_active_user)) -> JSONResponse:
    """
        ## Delete current user account

        This route deletes the account of the currently logged in user.

        ### Request body

        - **user** - User object

        ### Expected Response

        **204** - *The account has been deleted*
    """
    await user.delete()
    if check_user_exists(user):
        raise HTTPException(status_code=500, detail="User was not deleted")
    info(f"Account #{user.id} has been deleted")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
