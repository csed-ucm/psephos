from beanie import PydanticObjectId
from unipoll_api.schemas import WorkspaceSchemas
from pydantic import BaseModel, ConfigDict



class Workspace(WorkspaceSchemas.Workspace):
    timer: str = ""
        

class Plugin:
    def __init__(self):
        print("Timer plugin init")
        WorkspaceSchemas.Workspace = Workspace
        
        # from unipoll_api.routes.v2.workspaces import get_workspace
        # get_workspace.response_model = Workspace
        # WorkspaceSchemas.Workspace.add_field("timer", str)
    
    async def run(self, action, input):
        print("Timer plugin running")
        print(f"Action: {action}")
        print(f"Input: {input}")
        # print(f"Args: {args}")
        # print(f"Keyword Args: {kwargs}")
        res = await action
        res.timer = "Timer plugin"
        res.name = "Workspace updated by timer"
        # res.update({"timer": "Timer plugin"})
        # res.timer = "Timer plugin"
        # res["timer"] = "Timer plugin"
        return res