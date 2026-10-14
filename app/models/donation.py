from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, CommonMixin


class Donation(CommonMixin, Base):
    comment: Mapped[str | None] = mapped_column(
        Text,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user'),
        nullable=True
    )

    def __repr__(self):
        return (
            f'Пожертвование внесено{self.create_date}'
            f', освоено {self.close_date}'
        )
