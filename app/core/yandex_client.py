import httpx
from typing import Optional

from fastapi import HTTPException, status

from app.constants import YA_FOLDER


class YandexDiskClient:
    """
    Клиент для Яндекс Диска
    """
    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk'
        self.headers = {'Authorization': f'OAuth {token}'}
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30)
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        if self._client:
            await self._client.aclose()

    async def create_excel_file(
            self,
            title: str,
            folder: str = YA_FOLDER
    ) -> tuple[str, str]:

        await self._create_folder(folder)
        file_path = f'disk:/{folder}/{title}.xlsx'
        response = await self._client.get(
            f'{self.base_url}/resources/upload',
            headers=self.headers,
            params={"path": file_path, 'overwrite': 'true'}
        )
        response.raise_for_status
        data = response.json()
        upload_url = data.get('href')
        if not upload_url:
            raise ValueError("Не удалось получить ссылку для загрузки")

        return upload_url, file_path

    async def upload_file(
            self,
            upload_url: str,
            content: bytes
    ):
        response = await self._client.put(
            upload_url,
            content=content,
            headers={"Content-Type": (
                "application/vnd.openxmlformats"
                "-officedocument.spreadsheetml.sheet"
            )}
        )
        response.raise_for_status()

    async def publish_file(
            self,
            file_path: str
    ) -> str:
        response = await self._client.put(
            f'{self.base_url}/resources/publish/',
            headers=self.headers,
            params={'path': file_path}
        )
        response.raise_for_status

        response = await self._client.get(
            f'{self.base_url}/resources',
            headers=self.headers,
            params={'path': file_path}
        )
        data = response.json()
        public_url = data.get('public_url')
        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Ссылка не была получена со стороны Яндекс Диска"
            )
        return public_url

    async def _create_folder(
            self, folder: str
    ):
        try:
            await self._client.put(
                f'{self.base_url}/resources',
                headers=self.headers,
                params={'path': f'disk:/{folder}'}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 409:
                raise


async def get_yandex_client():
    """Dependency для получения клиента Яндекс Диска"""
    from app.core.config import settings

    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Яндекс Диск не настроен. Пожалуйста, "
                   "добавьте YANDEX_DISK_TOKEN в .env-файл"
        )

    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
