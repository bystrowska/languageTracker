from datetime import datetime

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
        Project(**Project.schema()["example_no_id"], id=123),
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
    return Project(**Project.schema()["example_no_id"], id=project_id)


"""
Get children
Get sub-projects for project_id
"""


@app.get("/children/{project_id}")
async def get_children(project_id: int) -> list[Project]:
    return [
        Project(**Project.schema()["example"]),
        Project(**Project.schema()["example_no_id"], id=123),
    ]


"""
Get parent
Get parent project for project id or None if top lvl
"""


async def get_parent(project_id: int) -> Project | None:
    pass
    pass


"""
Create new project
"""


@app.post("/project")
async def create_project(project: Project) -> Project:
    project.id = 111
    project.created = datetime.now()
    project.last_worked = None
    project.total_time = 0
    return project


"""
Update existing project
"""


@app.put("/project/{project_id}")
async def update_project(project_id: int, project: Project) -> Project:
    project.id = project_id
    return project
