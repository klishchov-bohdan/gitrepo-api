from app.models import Author
from app.utils.repo import SQLAlchemyRepository


class AuthorRepo(SQLAlchemyRepository):
    model = Author
