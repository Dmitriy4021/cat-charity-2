from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
            name: str,
            session: AsyncSession) -> Optional[int]:
        project_id_result = await session.execute(
            select(CharityProject.id)
            .where(CharityProject.name == name)
        )
        project_id = project_id_result.scalars().first()
        return project_id


charity_project_crud = CRUDCharityProject(CharityProject)
