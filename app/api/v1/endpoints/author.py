from fastapi import APIRouter, status

from app.api.deps import UOWDependency
from app.exceptions import AuthorNotFoundError, BadRequestError, DataNotFound
from app.schemas.author import AuthorBaseSchema, AuthorResp, SimpleAuthorResp
from app.services.author import AuthorService

router = APIRouter()


@router.get('/{author_id}',
            response_model=AuthorResp,
            status_code=status.HTTP_200_OK,
            description='Get and return Author by id',
            summary='Get Author')
async def get_author(author_id: int, uow: UOWDependency):
    try:
        author = await AuthorService(uow=uow).get_one(author_id=author_id)
        return author
    except DataNotFound:
        raise AuthorNotFoundError()
    except Exception:
        raise BadRequestError()


@router.get('/',
            response_model=list[AuthorResp],
            status_code=status.HTTP_200_OK,
            description='Get and return all Authors',
            summary='Get Authors')
async def get_authors(uow: UOWDependency):
    try:
        authors = await AuthorService(uow=uow).get_all()
        return authors
    except Exception:
        raise BadRequestError()


@router.post('/',
             response_model=SimpleAuthorResp,
             status_code=status.HTTP_201_CREATED,
             description='Create and return new Author id',
             summary='Create new Author')
async def create_author(author: AuthorBaseSchema, uow: UOWDependency):
    try:
        created_author = await AuthorService(uow=uow).create(author=author)
        return created_author
    except Exception:
        raise BadRequestError()


@router.patch('/{author_id}',
              response_model=SimpleAuthorResp,
              status_code=status.HTTP_200_OK,
              description='Update and return updated Author id',
              summary='Update Author')
async def update_author(author_id: int, author: AuthorBaseSchema, uow: UOWDependency):
    try:
        updated_author = await AuthorService(uow=uow).update(author_id=author_id, author=author)
        return updated_author
    except DataNotFound:
        raise AuthorNotFoundError()
    except Exception:
        raise BadRequestError()


@router.delete('/{author_id}',
               response_model=SimpleAuthorResp,
               status_code=status.HTTP_200_OK,
               description='Delete and return deleted Author id',
               summary='Delete Author')
async def delete_author(author_id: int, uow: UOWDependency):
    try:
        deleted_author = await AuthorService(uow=uow).delete(author_id=author_id)
        return deleted_author
    except DataNotFound:
        raise AuthorNotFoundError()
    except Exception:
        raise BadRequestError()
