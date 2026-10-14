from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.db import SessionDep
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import (
    DonationCreate,
    DonationCreateDB,
    DonationDB,
    DonationUpdateDB,
)
from app.services.logic import recalculate_donation_amount


router = APIRouter()


@router.post(
    '/',
    response_model=DonationCreateDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)],
)
async def create_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: Annotated[User, Depends(current_user)],
) -> DonationDB:
    """
    ## Создание пожертвования.

    **Права**
    - Только для авторизованного пользователя.

    **Алгоритм:**
    1. Получает данные нового пожертвования.
    2. Добавляет дату создания.
    3. Создаёт пожертвование и связывает его с текущим пользователем.
    4. Перераспределяет средства между открытыми благотворительными проектами.
    5. Возвращает созданное пожертвование.
    """
    donation_data = donation.model_dump()
    donation_data['create_date'] = datetime.now()

    donation_for_create = DonationUpdateDB(**donation_data)

    new_donation = await donation_crud.create(
        donation_for_create,
        session,
        user,
    )

    await recalculate_donation_amount(session)

    return new_donation


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: SessionDep,
) -> list[DonationDB]:
    """
    ## Получение списка всех пожертвований.

    **Права**
    - Только для суперпользователя.

    **Алгоритм:**
    1. Получает список всех пожертвований из базы данных.
    2. Возвращает список пожертвований со всеми доступными полями.
    """
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    response_model_exclude={'__all__': {
        'user_id',
        'invested_amount',
        'close_date',
        'fully_invested'
    }},
)
async def get_my_donations(
    session: SessionDep,
    user: Annotated[User, Depends(current_user)],
) -> list[DonationDB]:
    """
    ## Получение списка собственных пожертвований.

    **Права**
    - Только для авторизованного пользователя.

    **Алгоритм:**
    1. Получает текущего пользователя.
    2. Находит все пожертвования, созданные этим пользователем.
    3. Исключает из ответа поля `user_id`, `invested_amount`,
       `close_date` и `fully_invested`.
    4. Возвращает список пожертвований текущего пользователя.
    """
    my_donations = await donation_crud.get_by_user(session, user)
    return my_donations
