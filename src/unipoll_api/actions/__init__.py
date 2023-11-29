from functools import wraps

from unipoll_api.plugin_manager import get_plugin_manager

plugin_manager = get_plugin_manager()


def plugins(f):
    @wraps(f)
    async def wrapper(*args, **kwds):
        # print("Action Wrapper")
        # print(f"Action: {f}")
        # print(f"Args: {args}")
        # print(f"Kwds: {kwds}")
        # print("\n")
        
        res = await plugin_manager.run_plugins(action=f(*args, **kwds))
        # print(f"\nWrapper Result: {res}")
        
        return res
    return wrapper