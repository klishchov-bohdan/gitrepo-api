from app.schemas.author import AuthorBaseSchema, AuthorResp, SimpleAuthorResp
from app.utils.uow import IUnitOfWork


class AuthorService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_one(self, author_id: int):
        async with self.uow:
            author_data = await self.uow.author_repo.find_one(id=author_id)
            await self.uow.commit()
        return AuthorResp.model_validate(author_data)

    async def get_all(self):
        async with self.uow:
            authors_data = await self.uow.author_repo.find_all()
            await self.uow.commit()
        return [AuthorResp.model_validate(author_data) for author_data in authors_data]

    async def create(self, author: AuthorBaseSchema) -> SimpleAuthorResp:
        author_dict = author.model_dump()
        async with self.uow:
            created_author = await self.uow.author_repo.add_one(data=author_dict)
            await self.uow.commit()
        return SimpleAuthorResp(author_id=created_author)

    async def update(self, author_id: int, author: AuthorBaseSchema) -> SimpleAuthorResp:
        author_dict = author.model_dump()
        async with self.uow:
            updated_author = await self.uow.author_repo.edit_one(id=author_id, data=author_dict)
            await self.uow.commit()
        return SimpleAuthorResp(author_id=updated_author)

    async def delete(self, author_id: int) -> SimpleAuthorResp:
        async with self.uow:
            updated_author = await self.uow.author_repo.delete_one(id=author_id)
            await self.uow.commit()
        return SimpleAuthorResp(author_id=updated_author)
