import pandas as pd
from datetime import date, timedelta
from pathlib import Path

TODAY = date.today()
LAST_MONTH = (TODAY.replace(day=1) - timedelta(days=1)).strftime('%B_%Y')
TWO_MONTH_AGO = (TODAY.replace(day=1) - timedelta(days=32))

BASE_DIR = Path('.')
FILES_DIR = BASE_DIR / 'files'

def xlsx_to_csv_converter(file_path):
    CSV_FILE_NAME = f'cashless_payments_{LAST_MONTH}.csv'
    csv_full_path = FILES_DIR / CSV_FILE_NAME
    data_xls = pd.read_excel(file_path, index_col=0)
    data_xls.to_csv(csv_full_path, encoding='cp1251', sep=';')
    return csv_full_path
