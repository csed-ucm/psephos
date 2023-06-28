import uvicorn
# from src import app

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    # NOTE:  You must pass the application as an import string to enable 'reload' or 'workers'.
    uvicorn.run("src.app:app", reload=True, host="0.0.0.0", port=8000)
