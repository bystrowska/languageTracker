from datetime import datetime

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: int | None = Field(description="Unique id of the project", default=None)
    name: str = Field(description="Name of the project, must be unique")
    created: datetime = Field(
        description="Date and time this project was created", default=datetime.now()
    )
    last_worked: datetime | None = Field(
        description="Date and time this project's total time was last updated (?)",
        default=None,
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
            "example_no_id": {
                "name": "Nuzbek",
                "created": "2010-01-01T12:30",
                "last_worked": "2012-04-10T21:20",
                "total_time": "60",
            },
            "example_new": {
                "name": "Rural Chinese Esperanto",
                "total_time": "0",
            },
        }
