from app.models import Author, RepositoryAuthor
from app.utils.repo import SQLAlchemyRepository


class RepositoryAuthorRepo(SQLAlchemyRepository):
    model = RepositoryAuthor
