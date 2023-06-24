from src.models.documents import Workspace
from src.schemas import workspace as WorkspaceSchemas


# Get all workspaces
async def get_all_workspaces() -> WorkspaceSchemas.WorkspaceList:
    workspace_list = []
    search_result = await Workspace.find_all().to_list()

    # Create a workspace list for output schema using the search results
    for workspace in search_result:
        workspace_list.append(WorkspaceSchemas.Workspace(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description))

    return WorkspaceSchemas.WorkspaceList(workspaces=workspace_list)
