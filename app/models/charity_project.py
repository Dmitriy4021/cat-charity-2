from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import NAME_MAX_LENGTH
from app.core.db import Base, CommonMixin


class CharityProject(CommonMixin, Base):

    name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    def __repr__(self):
        return (
            f'Проект {self.name} открыт {self.create_date},'
            f'закрыт {self.close_date}'
        )
