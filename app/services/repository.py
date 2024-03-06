from datetime import datetime

from app.schemas.repository import (
    RepositoryActivity,
    RepositoryBaseSchema,
    RepositoryResp,
    SimpleRepositoryResp,
    SortBy,
    SortStrategy,
)
from app.utils.uow import IUnitOfWork


class RepositoryService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_one(self, repository_id: int):
        async with self.uow:
            repository_data = await self.uow.repository_repo.find_one(id=repository_id)
            await self.uow.commit()
        return RepositoryResp.model_validate(repository_data)

    async def get_all(self):
        async with self.uow:
            repositories_data = await self.uow.repository_repo.find_all()
            await self.uow.commit()
        return [RepositoryResp.model_validate(repository_data) for repository_data in repositories_data]

    async def get_top100_stars(self, sort_by: SortBy, sort_strategy: SortStrategy):
        async with self.uow:
            repositories_data = await self.uow.repository_repo.find_top100_stars(sort_by, sort_strategy)
            await self.uow.commit()
        return [RepositoryResp.model_validate(repository_data) for repository_data in repositories_data]

    async def get_activity(self, repository_name: str, owner: str, since: datetime, until: datetime):
        async with self.uow:
            repositories_data = await self.uow.repository_repo.get_activity(repository_name, owner, since, until)
            await self.uow.commit()
        return [RepositoryActivity.model_validate(repository_data) for repository_data in repositories_data]

    async def create(self, repository: RepositoryBaseSchema) -> SimpleRepositoryResp:
        repository_dict = repository.model_dump()
        async with self.uow:
            created_repository = await self.uow.repository_repo.add_one(data=repository_dict)
            await self.uow.commit()
        return SimpleRepositoryResp(repository_id=created_repository)

    async def update(self, repository_id: int, repository: RepositoryBaseSchema) -> SimpleRepositoryResp:
        repository_dict = repository.model_dump()
        async with self.uow:
            updated_repository = await self.uow.repository_repo.edit_one(id=repository_id, data=repository_dict)
            await self.uow.commit()
        return SimpleRepositoryResp(repository_id=updated_repository)

    async def delete(self, repository_id: int) -> SimpleRepositoryResp:
        async with self.uow:
            updated_repository = await self.uow.repository_repo.delete_one(id=repository_id)
            await self.uow.commit()
        return SimpleRepositoryResp(repository_id=updated_repository)
