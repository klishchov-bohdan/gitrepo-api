from typing import List

from sqlalchemy import TIMESTAMP, text, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class RepositoryAuthor(Base):
    __tablename__ = "repository_author"
    id: Mapped[str] = mapped_column(primary_key=True, index=True, unique=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repository.id", ondelete='CASCADE'))
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id", ondelete='CASCADE'))
    pushed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    author: Mapped["Author"] = relationship(back_populates="repositories")
    repository: Mapped["Repository"] = relationship(back_populates="authors")
    time_created: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    time_updated: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'),
                                                   onupdate=text('CURRENT_TIMESTAMP'))


class Repository(Base):
    __tablename__ = 'repository'
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    repo: Mapped[str] = mapped_column(nullable=False, unique=True)
    owner: Mapped[str] = mapped_column(nullable=False)
    position_cur: Mapped[int] = mapped_column(nullable=True)
    position_prev: Mapped[int] = mapped_column(nullable=True)
    stars: Mapped[int] = mapped_column(nullable=False)
    watchers: Mapped[int] = mapped_column(nullable=False)
    forks: Mapped[int] = mapped_column(nullable=False)
    open_issues: Mapped[int] = mapped_column(nullable=False)
    language: Mapped[str] = mapped_column(nullable=False)
    authors: Mapped[List["RepositoryAuthor"]] = relationship(back_populates="repository")
    time_created: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    time_updated: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'),
                                                   onupdate=text('CURRENT_TIMESTAMP'))


class Author(Base):
    __tablename__ = 'author'
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    repositories: Mapped[List["RepositoryAuthor"]] = relationship(back_populates="author")
    time_created: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    time_updated: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'),
                                                   onupdate=text('CURRENT_TIMESTAMP'))
