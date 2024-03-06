from app.models import RepositoryAuthor
from app.utils.repo import SQLAlchemyRepository


class RepositoryAuthorRepo(SQLAlchemyRepository):
    model = RepositoryAuthor
