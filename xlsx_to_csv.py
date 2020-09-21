import datetime
import pandas as pd
from pathlib import Path

FIRST_DAY_OF_MONTH = datetime.datetime.today().replace(day=1)
LAST_MONTH = (FIRST_DAY_OF_MONTH - datetime.timedelta(days=1)).strftime('%B_%Y')

BASE_DIR = Path('.')
FILES_DIR = BASE_DIR / 'files'

def xlsx_to_csv_converter(file_path):
    CSV_FILE_NAME = f'cashless_payments_{LAST_MONTH}.csv'
    csv_full_path = FILES_DIR / CSV_FILE_NAME
    data_xls = pd.read_excel(file_path, index_col=0)
    data_xls.to_csv(csv_full_path, encoding='cp1251', sep=';')
    return csv_full_path