from beanie import Document, after_event, Insert, Link
from pydantic import Field
from app.models.user import User
from app.utils import colored_dbg
from app.schemas.workspace import WorkspaceID


class Workspace(Document):
    """ Workspace model, based on Beanie Document class. This model is used to store information about workspaces.
        The model also contains methods specific to the workspace. 
        The owner and members are stored as links to the User model, which can be fetched to get the user data.

    Parameters:
        id (WorkspaceID): id of the workspace to be used internally and as the primary key in the database
        name (str): Name of the workspace
        description (str): Description of the workspace
        owner (Link[User]): Link to the owner of the workspace
        members  (list[Link[User]]): List of links to the members of the workspace
    """

    id: WorkspaceID = Field(default_factory=WorkspaceID, alias="_id")
    name: str = Field(default="", min_length=3, max_length=50,
                      regex="^[A-Z][A-Za-z]{2,}([ ]([0-9]+|[A-Z][A-Za-z]*))*$")
    description: str = Field(default="", title="Description", max_length=300)
    owner: Link[User] = Field(title="Owner", description="Owner of the workspace")
    members: list[Link[User]] = []

    @after_event(Insert)
    async def workspace_created(self) -> None:
        colored_dbg.info(
            f'New workspace "{self.name}" ({self.id}) has been created')