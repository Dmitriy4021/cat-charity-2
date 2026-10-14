from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from app.core.config import settings


class Base(DeclarativeBase):
    pass


class CommonMixin():

    __table_args__ = (
        CheckConstraint('full_amount > 0'),
        CheckConstraint('invested_amount <= full_amount'),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    full_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    invested_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    fully_invested: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    close_date: Mapped[datetime | None] = mapped_column(
        DateTime,
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
