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

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ) -> list[CharityProject]:
        closed_projects_result = await session.execute(
            select(CharityProject)
            .where(CharityProject.fully_invested.is_(True))
            # .order_by(CharityProject.close_date - CharityProject.create_date)
        )
        closed_projects = closed_projects_result.scalars().all()
        closed_projects.sort(
            key=lambda project: project.close_date - project.create_date
        )
        return closed_projects


charity_project_crud = CRUDCharityProject(CharityProject)
