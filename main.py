from enum import Enum
from typing import Any

from fastapi import Body, Cookie, FastAPI, File, Form, Header, Path, Query, status, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, HttpUrl, EmailStr

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
    name: str = Field(default="Item")
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
                        "url": "https://url.com", # url needs protocol
                        "name": "pretty image",
                    }
                ],
            }
        }

class CarItem(Item):
    name = "Car"
    price: float = 9.99 # idk why but you need type annotation for it to work

class PlaneItem(Item):
    name = "Plane"
    price: float = 10_000_000

class BaseUser(BaseModel):
    username: str = Field(example="thebestuser")
    email: EmailStr
    full_name: str | None = Field(default=None, example="Best User")

class UserIn(BaseUser):
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "koki",
                "password": "Tyskasmierdzi",
                "email": "koki@koki.koki",
                "full_name": "Eda-Weda TysTys"
            }
        }

class UserOut(BaseUser):

    class Config:
        schema_extra = {
            "example": {
                "username": "koki",
                "email": "koki@koki.koki",
                "full_name": "Eda-Weda TysTys"
            }
        }

class UserDB(BaseUser):
    hashed_password: str

app = FastAPI()

# items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
items_db = [Item(name="Foo", price=12.99), Item(name="Bar", price=3.49), Item(name="Baz", price=3.33)]

@app.get("/", status_code=status.HTTP_418_IM_A_TEAPOT)
async def root(
    user_agent: str | None = Header(default=None), # this is the user-agent thing that the browser sets
    # user_agent gets auto converted to user-agent but can disable by setting convert_underscores=False
    x_token: list[str] | None = Header(default=None),
):
    msg = {"message": "Hello " + (user_agent if user_agent else "world")}
    if x_token:
        msg.update({"x_token": x_token})
    return msg

@app.get("/tutorial/projects/{project_id}", status_code=status.HTTP_418_IM_A_TEAPOT)
async def get_project(project_id: int, q: str | None = None, short: bool = False):
    project = {"item_id": project_id}
    if q:
        project.update({"q": q})
    if not short:
        project.update(
            {"desc": "This is a description idk what to write"}
        )
    return project

@app.get("/tutorial/users/{user_id}/items/{item_id}", status_code=status.HTTP_418_IM_A_TEAPOT)
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

@app.get("/tutorial/item/{item_id}", response_model_exclude_none=True, status_code=status.HTTP_418_IM_A_TEAPOT)
async def read_item(
    *, # now all others args have to be called as keyword args
    item_id: int = Path(title="The ID of the item to get", ge=1, lt=100),
    q: str | None = Query(default=None),
    ads_id: str | None = Cookie(default=None), # needs to be explicitly declared as cookie, otherwise defaults to path param
    ) -> CarItem | PlaneItem:
    if item_id%2:
        item = CarItem(description=q)
    else:
        item = PlaneItem(description=q)
    if ads_id:
        print("ads_id: " + ads_id)
    return item

@app.get("/tutorial/models/{model_name}", status_code=status.HTTP_418_IM_A_TEAPOT)
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/tutorial/files/{file_path:path}", status_code=status.HTTP_418_IM_A_TEAPOT)
async def read_file(file_path: str):
    if file_path is "":
        return {"message": "empty file path"}
    return {"file_path": file_path}

@app.get("/tutorial/items/", status_code=status.HTTP_418_IM_A_TEAPOT)
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
) -> list[Item]:
    results = [items_db[x] for x in i]
    if q:
        for result in results:
            result.update({"q": q})
    return results

# request with body
@app.post("/tutorial/items/", response_model_exclude_unset=True, status_code=status.HTTP_418_IM_A_TEAPOT)
async def create_item(item: Item) -> Item:
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item

# request with body and path and query parameters
# if in path detected as path arg
# if not in path and singular type (int, float...) -> query arg
# if there's a model for that type -> request body
'''
@app.put("/tutorial/items/{item_id}")
async def create_item(item_id: int, item: Item, q: str | None = None):
    result =  {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
'''

@app.put("/tutorial/items/{item_id}", status_code=status.HTTP_418_IM_A_TEAPOT)
async def update_item(
    *,
    item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
    q: str | None = None, # query param is the default for singular types
    item: Item | None = None,
    user: UserOut | None = None,
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

@app.put("/tutorial/item", status_code=status.HTTP_418_IM_A_TEAPOT)
async def put_item(
    *,
    item: Item = Body(embed=True), # request will have key "key": val instead of just val
):
    results = {"item": item}
    return results

# dict with unknown keys / keys of specific type
# (json only supports str as keys but pydantic does the conversion)
@app.post("/tutorial/index-weights/", status_code=status.HTTP_418_IM_A_TEAPOT)
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

def fake_password_hasher(raw_password: str) -> str:
    return "hashhhh" + raw_password

def fake_save_user(user_in: UserIn) -> UserDB:
    hashed_password = fake_password_hasher(user_in.password)
    '''
     we unwrap a dict from user_in to be able to pass it as pairs of keys and values to the function
     so the below is eq to:
     UserDB(username=user_in_dict["username"], ...)
    '''
    user_db = UserDB(**user_in.dict(), hashed_password=hashed_password)
    print("User (fake) saved!")
    return user_db

@app.post("/tutorial/user/", status_code=status.HTTP_418_IM_A_TEAPOT)
async def create_user(user: UserIn) -> UserOut:
    user_saved = fake_save_user(user)
    return UserOut(**user_saved.dict())

@app.post("/tutorial/login/")
async def login(username: str = Form(), password: str = Form()): # can't have both body and form because encoding (idk why exactly but different encoding is used for forms)
    return {"username": username}

@app.post("/tutorial/files/", status_code=status.HTTP_201_CREATED)
async def create_file(
    file: bytes = File(), # the file gets stored in mem
    fileb: UploadFile = File(),
    token: str = Form(),
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

@app.post("/tutorial/uploadfile/", status_code=status.HTTP_201_CREATED)
async def create_upload_file(file: UploadFile = File(description="You need to use File() if you want to add desc, but the type can still be UploadFile so you get all the benefits")): # stored in mem only up to max size, rest on disc and you can get metadata from it
    contents = await file.read()
    return {"filename": file.filename, "contents": contents}

@app.post("/tutorial/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}

@app.get("/tutorial/uploadfiles/form/")
async def upload_files_form():
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)