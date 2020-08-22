import csv
import re
from email_report import send_email_report
from copy import deepcopy

MAIN_FILE_NAME = '2020_08_20_report_1.csv'
REFORMAT_FILE_NAME = '2020_08_20_report_2.csv'
CASHLESS_PAYMENTS_FILE = 'абонплата_jul_2020.csv'

COMMENTS = {
    'ТОВ СКІФ КИЇВ ЮА': 'Шота Руставелі 44, 6 — [Office44S6]',

    'Megogo: Максимальная': [
        {'addr': 'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]', 'sum': '197'},
        {'addr': 'Шота Руставелі 44, 5 — [KV249, KV113]', 'sum': '118.2'},
        {'addr': 'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]', 'sum': '157.6'},
        {'addr': 'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]', 'sum': '197'},
        {'addr': 'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]', 'sum': '197'},
        {'addr': 'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]', 'sum': '197'},
        {'addr': 'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]', 'sum': '197'},
    ],

    'ПАТ ДАТАГРУП': {
        '384,00': 'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]',
        '400,00': 'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]',
    }
}

def add_commission_to_portmone_csv_file(file_name):
    """Открываем файл и достаем с него данные в отсортированный словарь"""
    with open(file_name, encoding='cp1251', mode='r') as file_content:
        reader = csv.DictReader(file_content, delimiter=';')
        my_list = []

        for row in reader:
            """Добавляем к сумме комиссию и чистим поле комиссии"""
            comission = float(row['Комісія'].replace(',', '.').replace(' ', ''))
            summa = float(row['Сума'].replace(',', '.').replace(' ', '')) + comission
            row['Комісія'] = ''
            row['Сума'] = summa
            row['Сплачено'] = summa

            my_list.append(row)

    """Перезаписываем файл"""
    with open(file_name, encoding='cp1251', mode='w') as output_file:
        fieldnames = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума', 'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(my_list)
    print(f'Сумма обновлена и комиссия убрана в файле: {file_name}')


def reformat_portmone_csv_file(file_name, add_to_file_name):
    with open(file_name, encoding='cp1251', mode='r') as file_content:
        reader = csv.DictReader(file_content, delimiter=';')

        my_list = []

        """Индексы для выбора адреса из списка COMMENTS (комментарий к шаблону)"""
        megogo_index = 0

        for row in reader:
            """Убираем все ошибки оплаты"""
            if row['Статус'] == 'REJECTED':
                continue
            else:
                """Редактируем формат файла"""
                row['Статус'] = 'Сплачено'
                row['Компанія'] = row['Опис']
                row['Дата_сплати'] = row['Сплачено']
                row['Опис'] = 'Оплата за телекомунікаційні послуги'

                """Убриаем лишние кавычки"""
                row['Компанія'] = re.sub(r'[\"\'\»\«\“\”]', '', row['Компанія'])

                """Проставляем для каждой компании свой адрес"""
                if row['Компанія'] == 'Megogo: Максимальная':
                    row['Коментар'] = COMMENTS[row['Компанія']][megogo_index]['addr']
                    row['Сума'] = COMMENTS[row['Компанія']][megogo_index]['sum']
                    row['Сплачено'] = row['Сума']
                    megogo_index += 1

                elif row['Компанія'] == 'ПАТ ДАТАГРУП':
                    row['Коментар'] = COMMENTS[row['Компанія']][row['Сума']]
                else:
                    row['Коментар'] = COMMENTS[row['Компанія']]
                comission = float(row['Комісія'].replace(',', '.').replace(' ', ''))
                summa = float(row['Сума'].replace(',', '.').replace(' ', '')) + comission
                row['Комісія'] = ''
                row['Сума'] = summa
                row['Сплачено'] = summa

                my_list.append(row)

                if row['Сума'] == 118.2:
                    new_row = deepcopy(row)
                    new_row['Коментар'] = 'Шота Руставелі 44, 70 — [KV243]'
                    new_row['Сума'] = 78.8
                    new_row['Сплачено'] = 78.8
                    my_list.append(new_row)
                elif row['Сума'] == 157.6:
                    new_row = deepcopy(row)
                    new_row['Коментар'] = 'Шота Руставелі 44, 41 — [KV392]'
                    new_row['Сума'] = 39.4
                    new_row['Сплачено'] = 39.4
                    my_list.append(new_row)

    """Добавляем изменения в файл, указанный в переменной add_to_file_name"""
    with open(add_to_file_name, encoding='cp1251', mode='a') as output_file:
        fieldnames = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума', 'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
        writer.writerows(my_list)
    print(f'Данные из файла: {file_name} добавлены в файл: {add_to_file_name}')

def add_cashless_payments(write_file, read_file):
    with open(read_file, encoding='cp1251', mode='r') as in_file:
        reader = csv.DictReader(in_file, delimiter=';')

        with open(write_file, encoding='cp1251', mode='a') as out_file:
            fieldnames = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума',
                          'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']

            writer = csv.DictWriter(out_file, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
            writer.writerows(reader)

    print(f'Данные из файла: {read_file} добавлены в файл: {write_file}')

def total_file_sum(file_name, text_for_filed):
    with open(file_name, encoding='cp1251', mode='r') as in_file:
        reader = csv.DictReader(in_file, delimiter=';')
        total = sum([float(row["Сума"]) for row in reader])
        print(f'{text_for_filed}: {total}')
    return total


def main():
    add_commission_to_portmone_csv_file(MAIN_FILE_NAME)
    reformat_portmone_csv_file(REFORMAT_FILE_NAME, MAIN_FILE_NAME)
    portmone_small_sum = total_file_sum(MAIN_FILE_NAME, 'Сумма Portmone Small')
    cashless_payments_sum = total_file_sum(CASHLESS_PAYMENTS_FILE, 'Сумма безналичных платежей')
    add_cashless_payments(MAIN_FILE_NAME, CASHLESS_PAYMENTS_FILE)
    total_sum = total_file_sum(MAIN_FILE_NAME, 'Сумма итого файла')
    send_report_to_mail = input('Отправить файл по почте? (y/n): ')
    if send_report_to_mail == 'y':
        send_email_report(portmone_small_sum, cashless_payments_sum, total_sum, MAIN_FILE_NAME)


if __name__ == '__main__':
    main()
