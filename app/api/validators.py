from datetime import datetime
from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)


async def check_name_dublicate(
        session: AsyncSession,
        project_name: CharityProjectCreate | None = None,
        obj_db: CharityProjectDB | None = None,
):
    if project_name is None:
        return

    if obj_db is not None and project_name == obj_db.name:
        return

    project_id = await charity_project_crud.get_project_id_by_name(
        project_name,
        session,
    )
    if project_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProjectUpdate:
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Страница с проектом не найдена.'
        )
    return charity_project


async def check_project_status(
        db_obj: CharityProjectDB,
        session: AsyncSession,
):
    project_status = db_obj.fully_invested
    if project_status is True:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Закрытый проект нельзя редактировать!"
        )


async def check_invested_amount(
        obj_in: CharityProjectUpdate,
        db_obj: CharityProjectDB,
        session: AsyncSession,
) -> CharityProjectDB:

    if obj_in.full_amount is None:
        return

    if db_obj.invested_amount > obj_in.full_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=(
                "Нелья установить значение full_amount меньше уже вложенной"
                " суммы."
            )
        )
    elif db_obj.invested_amount == obj_in.full_amount:
        db_obj.fully_invested = True
        db_obj.close_date = datetime.now()

    return db_obj


def check_availability_invested_amount(
        db_obj: CharityProjectDB
):
    if db_obj.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="В проект были внесены средства, не подлежит удалению!"
        )
