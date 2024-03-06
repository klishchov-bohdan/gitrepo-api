from datetime import datetime
from typing import List

from fastapi import APIRouter, status

from app.api.deps import UOWDependency
from app.exceptions import RepositoryNotFoundError, DataNotFound, BadRequestError
from app.schemas.repository import SimpleRepositoryResp, RepositoryBaseSchema, RepositoryResp, SortBy, SortStrategy, \
    RepositoryActivity
from app.services.repository import RepositoryService

router = APIRouter()


@router.get('/{repository_id}',
            response_model=RepositoryResp,
            status_code=status.HTTP_200_OK,
            description='Get and return Repository by id',
            summary='Get Repository')
async def get_repository(repository_id: int, uow: UOWDependency):
    try:
        repository = await RepositoryService(uow=uow).get_one(repository_id=repository_id)
        return repository
    except DataNotFound:
        raise RepositoryNotFoundError()
    except Exception:
        raise BadRequestError()


@router.get('/',
            response_model=List[RepositoryResp],
            status_code=status.HTTP_200_OK,
            description='Get and return all Repositories',
            summary='Get Repositories')
async def get_repositories(uow: UOWDependency):
    try:
        repositories = await RepositoryService(uow=uow).get_all()
        return repositories
    except Exception:
        raise BadRequestError()


@router.get('/top100/',
            response_model=List[RepositoryResp],
            status_code=status.HTTP_200_OK,
            description='Get and return top 100 Repositories by stars',
            summary='Get top 100 Repositories')
async def get_top100_repositories(sort_by: SortBy, sort_strategy: SortStrategy, uow: UOWDependency):
    try:
        repositories = await RepositoryService(uow=uow).get_top100_stars(sort_by=sort_by, sort_strategy=sort_strategy)
        return repositories
    except Exception:
        raise BadRequestError()


@router.get('/{owner}/{repo}/activity/',
            response_model=List[RepositoryActivity],
            status_code=status.HTTP_200_OK,
            description='Get and return Repository activity',
            summary='Get Repository activity')
async def get_repository_activity(owner: str, repo: str, since: datetime, until: datetime, uow: UOWDependency):
    try:
        repositories = await RepositoryService(uow=uow).get_activity(repository_name=repo, owner=owner, since=since, until=until)
        return repositories
    except Exception:
        raise BadRequestError()


@router.post('/',
             response_model=SimpleRepositoryResp,
             status_code=status.HTTP_201_CREATED,
             description='Create and return new Repository id',
             summary='Create new Repository')
async def create_repository(repository: RepositoryBaseSchema, uow: UOWDependency):
    try:
        created_repository = await RepositoryService(uow=uow).create(repository=repository)
        return created_repository
    except Exception:
        raise BadRequestError()


@router.patch('/{repository_id}',
              response_model=SimpleRepositoryResp,
              status_code=status.HTTP_200_OK,
              description='Update and return updated Repository id',
              summary='Update Repository')
async def update_repository(repository_id: int, repository: RepositoryBaseSchema, uow: UOWDependency):
    try:
        updated_repository = await RepositoryService(uow=uow).update(repository_id=repository_id, repository=repository)
        return updated_repository
    except DataNotFound:
        raise RepositoryNotFoundError()
    except Exception:
        raise BadRequestError()


@router.delete('/{repository_id}',
               response_model=SimpleRepositoryResp,
               status_code=status.HTTP_200_OK,
               description='Delete and return deleted Repository id',
               summary='Delete Repository')
async def delete_repository(repository_id: int, uow: UOWDependency):
    try:
        deleted_repository = await RepositoryService(uow=uow).delete(repository_id=repository_id)
        return deleted_repository
    except DataNotFound:
        raise RepositoryNotFoundError()
    except Exception:
        raise BadRequestError()
