from abc import ABC, abstractmethod

from app.repos.author import AuthorRepo
from app.repos.repository import RepositoryRepo
from app.repos.repository_author import RepositoryAuthorRepo


class IUnitOfWork(ABC):
    repository_repo: RepositoryRepo
    author_repo: AuthorRepo
    repository_author_repo: RepositoryAuthorRepo

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork:
    def __init__(self, session_maker):
        self.session_factory = session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.repository_repo = RepositoryRepo(self.session)
        self.author_repo = AuthorRepo(self.session)
        self.repository_author_repo = RepositoryAuthorRepo(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
