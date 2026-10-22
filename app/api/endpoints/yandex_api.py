from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.api.validators import check_closed_projects
from app.core.db import SessionDep
from app.core.user import current_superuser
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.services.yandex_api import create_simple_report


router = APIRouter()


@router.post(
    '/',
    dependencies=[Depends(current_superuser)],
    response_model=str,
    summary="Создать Excel-отчёт на Яндекс Диске",
    description="""
    Создаёт Excel-файл с отчётом по срокам закрытия проектов.
    Файл сохраняется на Яндекс Диске в папке "QRKot Reports"
    и становится доступен по публичной ссылке.

    Требуются права суперпользователя.
    """
)
async def get_report(
    session: SessionDep,
    yandex_client: YandexDiskClient = Depends(get_yandex_client)
) -> str:
    """
    Создание отчёта в Excel-файле на Яндекс Диске
    """
    closed_projects = await check_closed_projects(session)

    try:
        public_url = await create_simple_report(yandex_client, closed_projects)

        return public_url

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании отчёта: {str(e)}"
        )
