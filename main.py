import os
import re
import csv

from datetime import date, timedelta
from locale import atof, setlocale, LC_TIME, LC_NUMERIC
from copy import deepcopy
from pathlib import Path

from xlsx_to_csv import xlsx_to_csv_converter
from email_report import send_email_report
from create_task import proceed_excel_task

setlocale(LC_NUMERIC, 'uk_UA.UTF-8')
setlocale(LC_TIME, 'en_US.UTF-8')
FIRST_DAY_OF_MONTH = date.today().replace(day=1)
LAST_MONTH = (FIRST_DAY_OF_MONTH - timedelta(days=1)).strftime('%B_%Y')

BASE_DIR = Path('.')
FILES_DIR = BASE_DIR / 'files'

MAIN_FP = list(FILES_DIR.glob('*report.csv'))[0]
REFORMAT_FP = list(FILES_DIR.glob('*report_2.csv'))[0]
EXCEL_FP = list(FILES_DIR.glob('абонплата*.xlsx'))[0]
RESULT_FILE = f'Portmone_Small_{LAST_MONTH}.csv'
RESULT_FP = FILES_DIR / RESULT_FILE

COMMENTS = {
	'ТОВ СКІФ КИЇВ ЮА': 'Шота Руставелі 44, 6 — [Office44S6]',
	'ТОВ В.О.К.С.': 'Басейна 19, 14 - [Office19B14]',
	'ПП МОНТАЖ ОХОРОННИХ СИСТЕМ': 'Басейна 19, 14 - [Office19B14]',
	'ПП БЕЗПЕЧНЕ МІСТО ХХІ': 'Басейна 19, 14 - [Office19B14]',

	'MEGOGO': [
		{'addr': 'Шота Руставелі 44, 5 — [KV249, KV113]', 'rule': lambda sum: round(sum / 5 * 3, 2)},
		{'addr': 'Шота Руставелі 44, 70 — [KV243]', 'rule': lambda sum: round(sum / 5 * 2, 2)},
		{'addr': 'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]', 'rule': lambda sum: round(sum / 5 * 4, 2)},
		{'addr': 'Шота Руставелі 44, 41 — [KV392]', 'rule': lambda sum: round(sum / 5 * 1, 2)},
		{'addr': 'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]'},
		{'addr': 'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]'},
		{'addr': 'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]'},
	],

	'ПАТ ДАТАГРУП': {
		77.44: 'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]',
		412.0: 'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]',
		432.6: 'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]',
	},
}

def add_commission_and_comments(file_path, result_file_path):
	"""Открываем файл и достаем с него данные в отсортированный словарь"""
	with open(file_path, encoding='cp1251', mode='r') as file_content:
		reader = csv.DictReader(file_content, delimiter=';')
		my_list = []
		megogo_index = 0

		for row in reader:

			"""Убриаем лишние кавычки"""
			row['Компанія'] = re.sub(r'[\"\'\»\«\“\”]', '', row['Компанія'])

			if row['Статус'] == 'Сплачений':
				row['Статус'] = 'Сплачено'

			"""Добавляем к сумме комиссию и чистим поле комиссии"""
			row['Сума'] = atof(row['Комісія']) + atof(row['Сума'])
			row['Сплачено'] = row['Сума']
			row['Комісія'] = ''

			"""Проверяем пустые комментарии к платежам"""
			megogo_payment = False

			if not row['Коментар']:
				if row['Компанія'] in ('MEGOGO', 'Megogo: Максимальная'):
					megogo_payment = True
					row['Коментар'] = COMMENTS['MEGOGO'][megogo_index]['addr']
					if 'rule' in COMMENTS['MEGOGO'][megogo_index]:
						original_sum = row['Сума']
						row['Сума'] = COMMENTS['MEGOGO'][megogo_index]['rule'](row['Сума'])
					row['Сплачено'] = row['Сума']
					megogo_index += 1

				elif row['Компанія'] == 'ПАТ ДАТАГРУП':
					row['Коментар'] = COMMENTS[row['Компанія']][row['Сума']]
				else:
					row['Коментар'] = COMMENTS[row['Компанія']]

			my_list.append(row)
			if megogo_payment:
				if row['Коментар'] == 'Шота Руставелі 44, 5 — [KV249, KV113]':
					new_row = deepcopy(row)
					new_row['Коментар'] = COMMENTS['MEGOGO'][megogo_index]['addr']
					new_row['Сума'] = COMMENTS['MEGOGO'][megogo_index]['rule'](original_sum)
					new_row['Сплачено'] = new_row['Сума']
					megogo_index += 1
					my_list.append(new_row)
					
				elif row['Коментар'] == 'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]':
					new_row = deepcopy(row)
					new_row['Коментар'] = COMMENTS['MEGOGO'][megogo_index]['addr']
					new_row['Сума'] = COMMENTS['MEGOGO'][megogo_index]['rule'](original_sum)
					new_row['Сплачено'] = new_row['Сума']
					megogo_index += 1
					my_list.append(new_row)

	"""Записываем в новый файл"""
	with open(result_file_path, encoding='cp1251', mode='w') as output_file:
		fields = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума', 'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']
		writer = csv.DictWriter(output_file, fieldnames=fields, delimiter=';', extrasaction='ignore')
		writer.writeheader()
		writer.writerows(my_list)


def refactor_csv(file_path, append_file):
	with open(file_path, encoding='cp1251', mode='r') as file_content:
		reader = csv.DictReader(file_content, delimiter=';')

		my_list = []

		"""Индексы для выбора адреса из списка COMMENTS (комментарий к шаблону)"""
		megogo_index = 0

		for row in reader:
			"""Убираем все ошибки оплаты"""
			if row['Статус'] == 'REJECTED':
				continue

			"""Редактируем формат файла"""
			row['Статус'] = 'Сплачено'
			row['Компанія'] = row['Опис']
			row['Дата_сплати'] = row['Сплачено']
			row['Опис'] = 'Оплата за телекомунікаційні послуги'

			"""Убриаем лишние кавычки"""
			row['Компанія'] = re.sub(r'[\"\'\»\«\“\”]', '', row['Компанія'])

			"""Добавляем к сумме комиссию и чистим поле комиссии"""
			row['Сума'] = atof(row['Комісія']) + atof(row['Сума'])
			row['Сплачено'] = row['Сума']
			row['Комісія'] = ''

			"""Проставляем для каждой компании свой адрес"""
			megogo_payment = False

			if row['Компанія'] in ('MEGOGO', 'Megogo: Максимальная'):
				megogo_payment = True
				row['Коментар'] = COMMENTS['MEGOGO'][megogo_index]['addr']
				if 'rule' in COMMENTS['MEGOGO'][megogo_index]:
					original_sum = row['Сума']
					row['Сума'] = COMMENTS['MEGOGO'][megogo_index]['rule'](row['Сума'])
				row['Сплачено'] = row['Сума']
				megogo_index += 1

			elif row['Компанія'] == 'ПАТ ДАТАГРУП':
				row['Коментар'] = COMMENTS[row['Компанія']][row['Сума']]
			else:
				row['Коментар'] = COMMENTS[row['Компанія']]

			my_list.append(row)

			if megogo_payment:
				if row['Коментар'] == 'Шота Руставелі 44, 5 — [KV249, KV113]':
					new_row = deepcopy(row)
					new_row['Коментар'] = COMMENTS['MEGOGO'][megogo_index]['addr']
					new_row['Сума'] = COMMENTS['MEGOGO'][megogo_index]['rule'](original_sum)
					new_row['Сплачено'] = new_row['Сума']
					megogo_index += 1
					my_list.append(new_row)

				elif row['Коментар'] == 'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]':
					new_row = deepcopy(row)
					new_row['Коментар'] = COMMENTS['MEGOGO'][megogo_index]['addr']
					new_row['Сума'] = COMMENTS['MEGOGO'][megogo_index]['rule'](original_sum)
					new_row['Сплачено'] = new_row['Сума']
					megogo_index += 1
					my_list.append(new_row)

	"""Добавляем изменения в основной файл"""
	with open(append_file, encoding='cp1251', mode='a') as output_file:
		fieldnames = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума', 'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']
		writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
		writer.writerows(my_list)

def add_cash_payments(read_file_path, write_file_path):
	with open(read_file_path, encoding='cp1251', mode='r') as in_file:
		reader = csv.DictReader(in_file, delimiter=';')

		with open(write_file_path, encoding='cp1251', mode='a') as out_file:
			fieldnames = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума',
						  'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']

			writer = csv.DictWriter(out_file, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
			writer.writerows(reader)
	os.remove(read_file_path)

def total_file_sum(file_path, text_for_filed):
	with open(file_path, encoding='cp1251', mode='r') as in_file:
		reader = csv.DictReader(in_file, delimiter=';')
		total = round(sum([float(row["Сума"]) for row in reader]), 2)
		print(f'{text_for_filed}: {total}')
	return total


def main():
	add_commission_and_comments(MAIN_FP, RESULT_FP)
	refactor_csv(REFORMAT_FP, RESULT_FP)
	portmone_small_sum = total_file_sum(RESULT_FP, 'Сумма Portmone Small')
	cash_payments_fp = xlsx_to_csv_converter(EXCEL_FP)
	cash_payments_sum = total_file_sum(cash_payments_fp, 'Сумма безналичных платежей')
	add_cash_payments(cash_payments_fp, RESULT_FP)
	total_sum = total_file_sum(RESULT_FP, 'Сумма итого файла')
	send_report_to_mail = input('Отправить файл по почте? (y/n): ')

	if send_report_to_mail == 'y':
		send_email_report(portmone_small_sum, cash_payments_sum, total_sum, RESULT_FP)
		proceed_excel_task(portmone_small_sum, cash_payments_sum, total_sum)
		

if __name__ == '__main__':
	main()
