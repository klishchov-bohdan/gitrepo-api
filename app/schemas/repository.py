from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class SortBy(str, Enum):
    repo = 'repo'
    owner = 'owner'
    stars = 'stars'
    watchers = 'watchers'
    forks = 'forks'
    open_issues = 'open_issues'
    language = 'language'


class SortStrategy(str, Enum):
    desc = 'DESC'
    asc = 'ASC'


class RepositoryBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    repo: str
    owner: str
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: str


class SimpleRepositoryResp(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    repository_id: int


class RepositoryResp(RepositoryBaseSchema):
    id: int
    position_cur: int | None
    position_prev: int | None


class RepositoryActivity(BaseModel):
    date: datetime
    commits: int
    authors: list[str]
