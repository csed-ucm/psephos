
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from unipoll_api import actions as Actions
from unipoll_api import documents as Documents
from unipoll_api import schemas as Schemas
from unipoll_api import dependencies as Dependencies
from unipoll_api import exceptions as Exceptions

router = APIRouter()


@router.get("", response_description="List of groups", response_model=Schemas.PolicySchemas.PolicyList)
async def get_policies(policy_holder: Annotated[Documents.ResourceID | None, Query()] = None,
                       workspace: Annotated[Documents.ResourceID | None, Query()] = None,
                       group: Annotated[Documents.ResourceID | None, Query()] = None):
    args = {}
    if policy_holder:
        args['policy_holder'] = await Documents.Account.get(policy_holder) or await Documents.Group.get(policy_holder)
    if workspace:
        args['resource'] = await Dependencies.get_workspace(workspace)
    elif group:
        args['resource'] = await Dependencies.get_group(group)

    return await Actions.PolicyActions.get_policies(**args)


@router.get("/{policy_id}", response_description="Policy")
async def get_policy(policy: Documents.Policy = Depends(Dependencies.get_policy)):
    try:
        return await Actions.PolicyActions.get_policy(policy=policy)
    except Exceptions.ResourceExceptions.APIException as e:
        raise HTTPException(status_code=e.code, detail=str(e))


# Create a new group
# 
# # @router.post("/",
#              status_code=201,
#              response_description="Member list",
#              response_model=Schemas.MemberSchemas.MemberList)
# async def add_members(input_data: Schemas.MemberSchemas.AddMembersRequest = Body(...)):
#     try:
#         if input_data.workspace:
#             resource = await Dependencies.get_workspace(input_data.workspace)
#         elif input_data.group:
#             resource = await Dependencies.get_group(input_data.group)
#         else:
#             raise Exceptions.ResourceExceptions.APIException(422, "Either Workspace or Group must be specified")

#         return await Actions.MembersActions.add_members(resource, input_data.accounts)
#     except Exceptions.ResourceExceptions.APIException as e:
#         raise HTTPException(status_code=e.code, detail=str(e))
