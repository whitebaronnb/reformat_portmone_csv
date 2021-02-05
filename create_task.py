# -*- coding: utf-8 -*-
import os
import base64
from zeep import Client
from pathlib import Path
from datetime import date, timedelta


USER = os.getenv('MANTIS_USER')
PASW = os.getenv('MANTIS_PASS')

MONTH = ['Январь', 'Февраль', 'Март', 'Апрель',
         'Май', 'Июнь', 'Июль', 'Август',
         'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

FILES = [file for file in Path('./files').iterdir() if not file.as_posix().startswith('files/.')]

LAST_MONTH = date.today().replace(day=1) - timedelta(days=1)
MONTH = MONTH[LAST_MONTH.month - 1]
YEAR = LAST_MONTH.year

NOTE_TEXT = 'Таблицу за {} {} составил и отправил по email ЯГ\n' \
			'Сумма Portmone Small: {} грн\n' \
			'Сумма безналичных платежей: {} грн\n' \
			'Сумма итого файла: <b>{}</b> грн'

SUMMARY = f'Составление таблицы EXCEL для Portmone {MONTH} {YEAR}'

DESCRIPTION = 'Составить таблицу EXCEL, в которой будут данные по всем' \
			  'платежам вне ресурса Portmone\n' \
			  'Таблицу предоставить Ярославу Гамрецкому\n\n' \
			  'Заполнить файл со сводными показателями стоимостей'

CATEGORY = 'excel отчет абонплата'

WSDL = 'https://mantis.partnerguesthouse.com/api/soap/mantisconnect.php?wsdl'

client = Client(WSDL)

IssueData = client.get_type('ns0:IssueData')
ObjectRef = client.get_type('ns0:ObjectRef')
AccountData = client.get_type('ns0:AccountData')
AttachmentData = client.get_type('ns0:AttachmentData')
IssueNoteData = client.get_type('ns0:IssueNoteData')

project = ObjectRef(id=155)
status = ObjectRef(id=70)
handler = AccountData(id=106)
attachments = [AttachmentData(filename=file.name) for file in FILES]

def prepare_issue_data(project, category, summary, description, status, handler):
	issue_data = IssueData(
		project=project, 
		category=category,
		summary=summary,
		description=description,
		status=status,
		handler=handler
	)
	return issue_data

def new_task(issue_data):
	return client.service.mc_issue_add(USER, PASW, issue_data)

def get_task_id_from_summary(summary):
	task = client.service.mc_issue_get_id_from_summary(USER, PASW, summary)
	return task

def issue_attachment_add(issue_id, name, file_type, content):
	client.service.mc_issue_attachment_add(USER, PASW, issue_id, name, file_type, content)

def issue_note_add(issue_id, note):
	notes = client.service.mc_issue_get(USER, PASW, issue_id).notes
	if notes and bool(map(lambda n: n.reporter.name == 'borovik.n', notes)):
		for existing_note in notes:
			if existing_note.reporter.name == 'borovik.n':
				note.id = existing_note.id
				client.service.mc_issue_note_update(USER, PASW, note)
				break
	else:
		client.service.mc_issue_note_add(USER, PASW, issue_id, note)

def issue_update(issue_id, issue_data):
	client.service.mc_issue_update(USER, PASW, issue_id, issue_data)

def proceed_excel_task(portmone_small, cash_payments, total):
	note = IssueNoteData(
		reporter=AccountData(id=172), 
		text=NOTE_TEXT.format(MONTH, YEAR, portmone_small, cash_payments, total)
	)
	issue_id = get_task_id_from_summary(SUMMARY)
	issue_data = prepare_issue_data(project, CATEGORY, SUMMARY, DESCRIPTION, status, handler, note)

	if issue_id != 0:
		print(f'\nExcel task already exists\n{issue_id}: {SUMMARY}')
		issue_update(issue_id, issue_data)
	elif issue_id == 0:
		issue_id = new_task(issue_data)
		print(f'\nNew excel task\n{issue_id}: {SUMMARY}')

	issue_note_add(issue_id, note)

	for file in FILES:
		with open(file, 'rb') as f:
			issue_attachment_add(issue_id, file.name, 'bug', f.read())
	print(f'\nFiles uploaded\n')

