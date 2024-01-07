import os
import random
import requests
from string import digits
from openpyxl import Workbook
from datetime import datetime
from openpyxl.styles import PatternFill, Font
from dateutil.relativedelta import relativedelta


class DataHandling:
    def get_last_acceptable_date(
        months_delta: int
    ) -> datetime:
        print("Defining the last month to look for news.")
        if months_delta <= 1:
            last_acceptable_date =  datetime.utcnow().replace(day=1, hour=0)
        else:
            last_acceptable_date = datetime.today() - relativedelta(months=months_delta-1)
        return last_acceptable_date

    def date_filter(
        date: str
    ) -> datetime:
        print("Converting the news' date format to datetime format.")
        months = {
            'Jan': 1,
            'Feb': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'Aug': 8,
            'Sept': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12
        }
        split_date = date.split(' ')
        month = months[split_date[0].replace('.','')] # the month sometimes is misspelled
        day = split_date[1].replace(',','')
        filtered_date = datetime.strptime(f"{day}/{month}/{split_date[2]}", "%d/%m/%Y")
        return filtered_date

    def download_file(
        url: str,
        date: str,
        query: str
    ) -> str:
        print("Downloading the new's image.")
        download_response = requests.get(
            url=url
        )
        if download_response and download_response.status_code != 200:
            return ''

        path = f'./output/{query}-image-{date}-{random.randint(100000,999999)}.png'
        open(path, "wb").write(download_response.content)

        return os.path.abspath(path)

    def build_sheet(
        extracted_data: list,
        sheet_name: str
    ) -> str:
        print("Building sheet with the extracted data.")
        header = [
            'picture_filename',
            'title',
            'description',
            'date',
            'search_phrase_count',
            'contains_money'
        ]
        header_len = len(header)
        header_cells = []

        for index in range(header_len):
            header_cells.append(f'{chr(index+65)}1')
        cell_number = str.maketrans('', '', digits)

        print(extracted_data)
        wb = Workbook()
        ws = wb.active

        fill_style = PatternFill(
            start_color='205792',
            end_color='205792',
            fill_type='solid'
        )

        font_style = Font(
            bold=True,
            size=12,
            color='FFFFFF',
            name='Calibri'
        )

        for index, cell in enumerate(header_cells):
            column = cell.translate(cell_number)
            ws[cell].fill = fill_style
            ws[cell].font = font_style
            ws[cell] = header[index]
            ws.column_dimensions[column].width = len(header[index]) + 25

            for index_row, process in enumerate(extracted_data):
                ws.cell(
                    column=index+1,
                    row=index_row+2,
                    value=process[header[index]]
                )

        sheet_path = f'./output/{sheet_name}.xlsx'
        wb.save(sheet_path)
        return sheet_path
