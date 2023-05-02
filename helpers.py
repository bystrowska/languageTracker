from datetime import datetime

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: int = Field(description="Unique id of the project")
    name: str = Field(description="Name of the project")
    created: datetime = Field(description="Date and time this project was created")
    last_worked: datetime = Field(
        description="Date and time this project's total time was last updated (?)"
    )
    total_time: int = Field(
        description="Total time spent on project in seconds"
    )  # or timedelta? who knows

    class Config:
        schema_extra = {
            "example": {
                "id": "666",
                "name": "Uzbek",
                "created": "2020-01-01T12:30",
                "last_worked": "2022-04-10T21:20",
                "total_time": "3600",
            },
            "example2": {
                "id": "999",
                "name": "Nuzbek",
                "created": "2010-01-01T12:30",
                "last_worked": "2012-04-10T21:20",
                "total_time": "60",
            },
        }
