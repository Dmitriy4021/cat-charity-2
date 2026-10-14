from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.charity_project import CharityProject
from app.models.donation import Donation
from app.schemas.charity_project import CharityProjectCreateDB
from app.schemas.donation import DonationUpdateDB


async def update_investment(
        obj,
        invested_amount: int,
        crud,
        schema,
        session: AsyncSession,
        fully_invested: bool = False,
):
    """
    ## Обновление суммы инвестиций в объекте.

    **Параметры:**
    - obj — объект пожертвования или благотворительного проекта.
    - invested_amount — новая сумма вложенных средств.
    - crud — CRUD-объект для обновления записи в базе данных.
    - schema — схема для валидации обновляемых данных.
    - session — асинхронная сессия базы данных.
    - fully_invested — признак полного финансирования объекта.

    **Алгоритм:**
    1. Подготовить данные с новой суммой вложенных средств.
    2. Если объект полностью профинансирован, установить соответствующий
       признак и дату закрытия.
    3. Создать объект схемы с обновлёнными данными.
    4. Обновить запись в базе данных через CRUD-метод.
    """
    data_in = {
        'invested_amount': invested_amount,
    }

    if fully_invested:
        data_in['fully_invested'] = True
        data_in['close_date'] = datetime.now()

    obj_in = schema(**data_in)
    await crud.update(obj, obj_in, session)


async def recalculate_donation_amount(
        session: AsyncSession,
):
    """
    ## Перераспределение средств пожертвований между проектами.

    **Параметры:**
    - session — асинхронная сессия базы данных.

    **Алгоритм:**
    1. Получить все незакрытые пожертвования в порядке их создания.
    2. Для каждого пожертвования вычислить оставшуюся сумму средств.
    3. Передать средства на распределение между открытыми проектами.
    4. Если пожертвование полностью распределено, обновить его сумму
       инвестиций и установить дату закрытия.
    5. Если средства распределены частично, обновить сумму инвестиций
       пожертвования и завершить обработку.

    **Возвращает:**
    Ничего. Изменяет записи пожертвований и проектов в базе данных.
    """
    open_donations_result = await session.execute(
        select(Donation)
        .where(Donation.fully_invested.is_(False))
        .order_by(Donation.create_date)
    )
    open_donations = open_donations_result.scalars().all()

    if open_donations:
        for open_donation in open_donations:
            donation_amount = (
                open_donation.full_amount - open_donation.invested_amount
            )
            surplus = await get_donation_amount(
                session,
                donation_amount=donation_amount
            )

            if surplus == 0:
                await update_investment(
                    open_donation,
                    open_donation.full_amount,
                    donation_crud,
                    DonationUpdateDB,
                    session,
                    fully_invested=True,
                )

            elif surplus != open_donation.full_amount:
                await update_investment(
                    open_donation,
                    open_donation.full_amount - surplus,
                    donation_crud,
                    DonationUpdateDB,
                    session,
                )
                break


async def get_donation_amount(
        session: AsyncSession,
        donation_amount: int
):
    """
    ## Распределение средств пожертвования между благотворительными проектами.

    **Параметры:**
    - session — асинхронная сессия базы данных.
    - donation_amount — сумма пожертвования, доступная для распределения.

    **Алгоритм:**
    1. Получить все незакрытые благотворительные проекты в порядке их создания.
    2. Если открытых проектов нет, вернуть всю доступную сумму.
    3. Последовательно распределять средства между проектами.
    4. Если оставшейся суммы достаточно для полного финансирования проекта,
       закрыть проект и установить дату закрытия.
    5. Если средств недостаточно для полного финансирования проекта,
       увеличить сумму его инвестиций на доступный остаток.
    6. Вернуть нераспределённый остаток пожертвования.

    **Возвращает:**
    Сумму пожертвования, которая осталась нераспределённой.
    """
    open_projects_result = await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested.is_(False))
        .order_by(CharityProject.create_date)
    )
    open_projects = open_projects_result.scalars().all()

    if open_projects == []:
        return donation_amount

    for open_project in open_projects:
        required_amount = (
            open_project.full_amount - open_project.invested_amount
        )

        if required_amount <= donation_amount:
            donation_amount -= required_amount

            await update_investment(
                open_project,
                open_project.full_amount,
                charity_project_crud,
                CharityProjectCreateDB,
                session,
                fully_invested=True,
            )

        elif required_amount > donation_amount:
            await update_investment(
                open_project,
                open_project.invested_amount + donation_amount,
                charity_project_crud,
                CharityProjectCreateDB,
                session,
            )
            donation_amount = 0
            break

    return donation_amount