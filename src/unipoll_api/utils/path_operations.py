from fastapi import Request
from unipoll_api.documents import ResourceID
from unipoll_api.utils.colored_dbg import print_error


# Extract resource from request
def extract_action_from_path(request: Request, extract_id: bool = True) -> str:
    # Extract path and operation_id from request
    try:
        return str(request["route"].name)
    except Exception as e:
        print_error("Error extracting resource from path: ", str(e))
        raise e


def extract_resourceID_from_path(request: Request) -> ResourceID:
    try:
        return ResourceID(request["path"].split("/")[2])
    except Exception as e:
        print_error("Error extracting resource ID from path: ", str(e))
        raise e
