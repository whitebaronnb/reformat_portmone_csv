import csv
import re

MAIN_FILE_NAME = '2020_08_20_report_1.csv'
REFORMAT_FILE_NAME = '2020_08_20_report_2.csv'
FILE_WITH_CASHLESS_OPERATIONS = 'абонплата_jul_2020.csv'

COMMENTS = {
    'ТОВ СКІФ КИЇВ ЮА': 'Шота Руставелі 44, 6 — [Office44S6]',

    'Megogo: Максимальная': [
        'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]',
        'Шота Руставелі 44, 5 — [KV249, KV113]',
        'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]',
        'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]',
        'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]',
        'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]',
        'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]',],

    'ФОП Цитович Олег Вадимович': [
        'Кловскьий Спуск 7, 191 — [KV911, KV912, KV913, KV914, KV915]',
        'Кловський Спуск 7, 195 — [KV951, KV952, KV953, KV954, KV955]',],

    'ТОВ В.О.К.С.': 'Басейна 19, 14  — [Office19B14]',

    'ПАТ ДАТАГРУП': [
        'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]',
        'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]'],
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
            row['Сплачено'] = row['Сума']

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
        citovich_index = 0

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
                    row['Коментар'] = COMMENTS[row['Компанія']][megogo_index]
                    megogo_index += 1

                elif row['Компанія'] == 'ФОП Цитович Олег Вадимович':
                    row['Коментар'] = COMMENTS[row['Компанія']][citovich_index]
                    citovich_index += 1

                elif row['Компанія'] == 'ПАТ ДАТАГРУП':
                    if row['Сума'] == '400,00':
                        row['Коментар'] = COMMENTS[row['Компанія']][0]
                    else:
                        row['Коментар'] = COMMENTS[row['Компанія']][1]
                else:
                    row['Коментар'] = COMMENTS[row['Компанія']]

                """Вводим сумму комиссии и суммируем её к оплате"""
                comission = float(row['Комісія'].replace(',', '.').replace(' ', ''))
                summa = float(row['Сума'].replace(',', '.').replace(' ', '')) + comission
                row['Комісія'] = ''
                row['Сума'] = summa
                row['Сплачено'] = row['Сума']

                my_list.append(row)

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


def main():
    add_commission_to_portmone_csv_file(MAIN_FILE_NAME)
    reformat_portmone_csv_file(REFORMAT_FILE_NAME, MAIN_FILE_NAME)
    add_cashless_payments(MAIN_FILE_NAME, FILE_WITH_CASHLESS_OPERATIONS)


if __name__ == '__main__':
    main()
