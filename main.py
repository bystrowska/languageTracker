from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    return {"project_id": project_id}