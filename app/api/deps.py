from typing import Annotated

from fastapi import Depends

from app.database import async_session_maker
from app.utils.uow import IUnitOfWork, UnitOfWork


def get_uow() -> UnitOfWork:
    return UnitOfWork(session_maker=async_session_maker)


UOWDependency = Annotated[IUnitOfWork, Depends(get_uow)]
