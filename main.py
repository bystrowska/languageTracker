from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

'''
data model from Pydantic gives code completion and other stuff
other than that basically a dict (?)
'''
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/projects/{project_id}")
async def get_project(project_id: int, q: str | None = None, short: bool = False):
    project = {"item_id": project_id}
    if q:
        project.update({"q": q})
    if not short:
        project.update(
            {"desc": "This is a description idk what to write"}
        )
    return project

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"desc": "This is a user's item blah blah"}
        )
    return item

@app.get("/items/{item_id}")
async def read_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return items_db[skip: skip + limit]

# request with body
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

# request with body and path and query parameters
# if in path detected as path arg
# if not in path and singular type (int, float...) -> query arg
# if there's a model for that type -> request body
@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: str | None = None):
    result =  {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result