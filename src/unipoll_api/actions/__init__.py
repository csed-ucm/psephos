from unipoll_api.plugins import run_plugins

from functools import wraps


def plugins(f):
    @wraps(f)
    async def wrapper(*args, **kwds):
        print("Action Wrapper")
        print(f"Action: {f}")
        print(f"Args: {args}")
        print(f"Kwds: {kwds}")
        print("\n")
        res = await run_plugins(action=f(*args, **kwds))
        print(f"\nWrapper Result: {res}")
        
        return res
    return wrapper