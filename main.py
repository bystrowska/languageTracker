from enum import Enum

from fastapi import Body, Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel, Field, HttpUrl

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

'''
data model from Pydantic gives code completion and other stuff
other than that basically a dict (?)
'''
class Image(BaseModel):
    url: HttpUrl
    name: str

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    ) # field works the same as Path / Query and has all the same params
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.3,
                "tax": 3.2,
                "tags": ["one", "two"],
                "images": [
                    {
                        "url": "url",
                        "name": "pretty image",
                    }
                ],
            }
        }

class User(BaseModel):
    username: str = Field(example="thebestuser")
    full_name: str | None = Field(default=None, example="Best User")

app = FastAPI()

items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/")
async def root(
    user_agent: str | None = Header(default=None), # this is the user-agent thing that the browser sets
    # user_agent gets auto converted to user-agent but can disable by setting convert_underscores=False
    x_token: list[str] | None = Header(default=None),
):
    msg = {"message": "Hello " + (user_agent if user_agent else "world")}
    if x_token:
        msg.update({"x_token": x_token})
    return msg

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

@app.get("/item/{item_id}")
async def read_items(
    *, # now all others args have to be called as keyword args
    item_id: int = Path(title="The ID of the item to get", ge=1, lt=100),
    q: str | None = Query(default=None),
    ads_id: str | None = Cookie(default=None), # needs to be explicitly declared as cookie, otherwise defaults to path param
    ):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if ads_id:
        results.update({"ads_id": ads_id})
    return results

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
async def read_items(
    i: list[int] = Query(default=[]), # this is query arg, but since it's a list it has to be declared explicitly with Query bc otherwise it would be treated as request body arg
    q: str | None = Query(
        default=None,
        alias="item-query",
        title="Query string",
        description="Query string that can only be 'fixedquery'",
        min_length=3,
        max_length=50,
        regex="^fixedquery$", # ^ -> starts with $ -> ends after
        deprecated=True

    )
):
    results = [items_db[x] for x in i]
    if q:
        for result in results:
            result.update({"q": q})
    return results

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
'''
@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item, q: str | None = None):
    result =  {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
'''

@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
    q: str | None = None, # query param is the default for singular types
    item: Item | None = None,
    user: User | None = None,
    importance: int = Body(),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    if user:
        results.update({"user": user})
    return results

@app.put("/item")
async def put_item(
    *,
    item: Item = Body(embed=True), # request will have key "key": val instead of just val
):
    results = {"item": item}
    return results

# dict with unknown keys / keys of specific type
# (json only supports str as keys but pydantic does the conversion)
@app.post("/index-weights/")
async def create_index_weights(
    weights: dict[int, float] = Body(
        description="int: float",
        examples={
            "good example": {
                "summary": "working example",
                "description": "it will work if you use it!",
                "value": {
                    4: 4.5,
                },
            },
            "bad example": {
                "summary": "invalid example",
                "description": "it won't work if you use it :(",
                "value": {
                    "not an int": 4,
                },
            },
        },
    )
):
    return weights