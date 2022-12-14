import uvicorn
import app

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run("app.app:app", reload=True, debug=True, host="0.0.0.0", port=8000)