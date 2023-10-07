from unipoll_api.documents import Workspace
from unipoll_api.schemas import WorkspaceSchemas


# Get all workspaces
async def get_all_workspaces() -> WorkspaceSchemas.WorkspaceList:
    workspace_list = []
    search_result = await Workspace.find_all().to_list()

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        workspace_list.append(WorkspaceSchemas.Workspace(**workspace.model_dump()))

    return WorkspaceSchemas.WorkspaceList(workspaces=workspace_list)
