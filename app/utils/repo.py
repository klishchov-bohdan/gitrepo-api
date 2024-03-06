from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DataNotFound


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def add_many(self, data: list[dict]):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model: Any = None

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def add_one(self, data: dict) -> int:
        column_names = ', '.join(data.keys())
        column_values = ', '.join([':' + key for key in data.keys()])
        stmt = text(f'''
            INSERT INTO {self.model.__tablename__} ({column_names}) 
            VALUES ({column_values})
            RETURNING id;
        ''')
        result = await self.session.execute(stmt, data)
        created_id = result.scalar_one()
        return created_id

    async def add_many(self, data: list[dict]):
        raise NotImplementedError

    async def find_all(self):
        stmt = text(f'''
                            SELECT *
                            FROM {self.model.__tablename__} 
                        ''')
        result = await self.session.execute(stmt)
        res_columns = result.keys()
        rows_values = result.all()
        return [dict(zip(res_columns, row_values)) for row_values in rows_values]

    async def find_one(self, id: int):
        try:
            stmt = text(f'''
                        SELECT *
                        FROM {self.model.__tablename__} 
                        WHERE id = {id}
                    ''')
            result = await self.session.execute(stmt)
            res_columns = result.keys()
            res_values = result.first()
            return dict(zip(res_columns, res_values))
        except NoResultFound as ex:
            raise DataNotFound(ex)
        except TypeError as ex:
            raise DataNotFound(ex)

    async def edit_one(self, id: int, data: dict):
        try:
            values_update = ', '.join([f'{key} = :{key}' for key in data.keys()])
            stmt = text(f'''
                        UPDATE {self.model.__tablename__} 
                        SET {values_update}
                        WHERE id = {id}
                        RETURNING id;
                    ''')
            result = await self.session.execute(stmt, data)
            updated_id = result.scalar_one()
            return updated_id
        except NoResultFound as ex:
            raise DataNotFound(ex)

    async def delete_one(self, id: int):
        try:
            stmt = text(f'''
                        DELETE FROM {self.model.__tablename__} 
                        WHERE id = {id}
                        RETURNING id;
                    ''')
            result = await self.session.execute(stmt)
            deleted_id = result.scalar_one()
            return deleted_id
        except NoResultFound as ex:
            raise DataNotFound(ex)
