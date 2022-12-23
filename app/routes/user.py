from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.models.user import User
from app.models.user_manager import current_active_user
from app.schemas.user import UserID, UserRead
# from beanie import PydanticObjectId
from app.exceptions import user as user_exceptions
from app.utils.user import get_user_groups
from app.utils.colored_dbg import info

# APIRouter creates path operations for user module
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


# List all groups that a user is a member of
@router.get("/groups",
            response_description="List all groups that a user is a member of")
async def list_user_groups(user_id: UserID | None = None,
                           user: User = Depends(current_active_user)) -> JSONResponse:
    if user_id:
        search = await User.find_one({"_id": user_id})
        if search:
            user = search
        else:
            raise user_exceptions.UserNotFound(user_id)

    # TODO: Consider using a proper model
    groups = await get_user_groups(user)
    return JSONResponse(groups)


# Delete current user account
@router.delete("/me",
               status_code=status.HTTP_204_NO_CONTENT,
               response_description="The account has been deleted")
async def delete_user(user: User = Depends(current_active_user)) -> JSONResponse:
    info(f"Account #{user.id} has been deleted")
    await user.delete()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
