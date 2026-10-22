import io
from datetime import timedelta, datetime

import xlsxwriter

from app.constants import (
    SEC_IN_HOUR,
    SEC_IN_MIN
)
from app.core.config import settings
from app.core.yandex_client import YandexDiskClient


def format_time_delta(delta: timedelta):
    if delta.days > 0:
        return f'{delta.days} дн. {delta.seconds // SEC_IN_HOUR} ч.'
    return (
        f'{delta.seconds // SEC_IN_HOUR} ч. '
        f'{(delta.seconds % SEC_IN_HOUR) // SEC_IN_MIN} мин.'
    )


async def create_simple_report(
        yandex_client: YandexDiskClient,
        charety_projects: list,
):
    now_date_time = datetime.now().strftime(settings.report_format)
    safe_filename = (
        f"Отчет_{now_date_time}"
        .replace(':', '-').replace(' ', '_').replace('/', '-')
    )

    upload_url, file_path = (
        await yandex_client.create_excel_file(safe_filename))

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Отчет')

    headers = ['Название проекта', 'Время сбора', 'Описание']

    title_format = workbook.add_format({
        'bold': True,
        'border': 0
    })
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': 'purple',
        'border': 1
    })
    cell_format = workbook.add_format({
        'border': 1
    })
    total_format = workbook.add_format({
        'bold': True,
        'border': 1
    })

    worksheet.merge_range('A1:C1', f"Отчет от {now_date_time}", title_format)

    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    for row, charety_project in enumerate(charety_projects, start=2):

        delta = format_time_delta(
            charety_project.close_date - charety_project.create_date
        )

        worksheet.write(row, 0, charety_project.name, cell_format)
        worksheet.write(row, 1, delta, cell_format)
        worksheet.write(row, 2, charety_project.description, cell_format)

    row_count = len(charety_projects)
    last_row = row_count + 2
    worksheet.merge_range(
        last_row, 0, last_row, 2,
        f'Всего проектов: {row_count}',
        total_format
    )

    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 60)

    workbook.close()
    output.seek(0)

    await yandex_client.upload_file(upload_url, output.getvalue())

    public_url = await yandex_client.publish_file(file_path)
    return public_url
