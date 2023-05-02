from fastapi import FastAPI

from helpers import Project

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


"""
Endpoints
"""

"""
Get projects
Returns a list of all projects
"""


@app.get("/projects")
async def get_projects() -> list[Project]:
    return [
        Project(**Project.schema()["example"]),
        Project(**Project.schema()["example2"]),
    ]


"""
Get project by id
Returns a dict with project properties
Properties:
- id
- name
- date created
- last worked
- total time
"""


@app.get("/project/{project_id}")
async def get_properties(project_id: int) -> Project:
    proj = Project(**Project.schema()["example"])
    proj.id = project_id
    return proj
