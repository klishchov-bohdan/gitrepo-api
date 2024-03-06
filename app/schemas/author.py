from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthorBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class SimpleAuthorResp(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    author_id: int


class AuthorResp(AuthorBaseSchema):
    id: int
