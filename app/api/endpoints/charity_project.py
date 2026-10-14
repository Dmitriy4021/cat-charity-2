from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.validators import (
    check_availability_invested_amount,
    check_invested_amount,
    check_name_dublicate,
    check_project_exists,
    check_project_status,
)
from app.core.db import SessionDep
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectCreateDB,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.logic import recalculate_donation_amount

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: SessionDep,
):
    """
    ## Создание нового благотворительного проекта.

    **Права**
    - Только для суперпользователя

    **Алгоритм:**
    1. Проверяет уникальность названия.
    2. Создаёт проект.
    3. Пересчитывает сумму пожертвований.
    """
    await check_name_dublicate(
        session,
        charity_project.name,
    )

    charity_project_data = charity_project.model_dump()
    charity_project_data['create_date'] = datetime.now()

    charity_project_for_create = CharityProjectCreateDB(
        **charity_project_data,
    )

    new_charity_project = await charity_project_crud.create(
        charity_project_for_create,
        session,
        commit=False
    )

    await recalculate_donation_amount(session)
    await session.commit()

    return new_charity_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_project(
    session: SessionDep
):
    """
    ## Получение всех благотворительных проектов

    **Права**
    - Для всех пользователей
    """
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep,
):
    """
    ## Обновление благотворительного проекта.

    **Права**
    - Только для суперпользователя

    **Алгоритм:**
    1. Проверяет существование проекта.
    2. Проверяет, что проект ещё не закрыт.
    3. Проверяет корректность новой суммы сбора.
    4. Проверяет уникальность нового названия.
    5. Обновляет данные проекта.
    """
    charity_project = await check_project_exists(
        project_id,
        session,
    )

    await check_project_status(charity_project, session)

    await check_invested_amount(
        obj_in,
        charity_project,
        session,
    )

    await check_name_dublicate(
        session,
        obj_in.name,
        charity_project,
    )

    updating_charity_project = await charity_project_crud.update(
        charity_project,
        obj_in,
        session,
    )
    return updating_charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def remove_charity_project(
    project_id: int,
    session: SessionDep,
) -> CharityProjectDB:
    """
    ## Удаление благотворительного проекта.

    **Права**
    - Только для суперпользователя

    **Алгоритм:**
    1. Проверяет существование проекта.
    2. Проверяет, что в проект не внесены пожертвования.
    3. Удаляет благотворительный проект.
    """
    charity_project = await check_project_exists(
        project_id,
        session,
    )
    check_availability_invested_amount(
        charity_project
    )
    charity_project = await charity_project_crud.remove(
        charity_project,
        session,
    )
    return charity_project
