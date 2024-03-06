from fastapi import APIRouter

from app.api.v1.endpoints import repository, author

api_router = APIRouter()
api_router.include_router(repository.router, prefix="/repos", tags=["Repository"])
api_router.include_router(author.router, prefix="/author", tags=["Author"])
