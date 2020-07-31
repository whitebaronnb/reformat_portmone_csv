import csv
import pprint
import re


def add_commission_to_portmone_csv_file(file_name):
    """Открываем файл и достаем с него данные в отсортированный словарь"""
    with open(file_name, encoding='cp1251', mode='r') as file_content:
        reader = csv.DictReader(file_content, delimiter=';')

        my_list = []

        for row in reader:
            """Меняем формат чисел"""
            row['Сума'] = re.sub(r'(\d),(\d)', r'\1.\2', row['Сума'])
            row['Комісія'] = re.sub(r'(\d),(\d)', r'\1.\2', row['Комісія'])

            """Меняем сумму на сумму с комиссией, и чистим поле комиссии"""
            row['Сума'] = float(row['Сума']) + float(row['Комісія'])
            row['Сума'] = "%.2f" % row['Сума']
            row['Сплачено'] = row['Сума']
            row['Комісія'] = ''

            my_list.append(row)


    """Перезаписываем файл"""
    with open(file_name, encoding='cp1251', mode='w') as output_file:
        fieldnames = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума', 'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(my_list)
        print('------------------------------------------------------------------')
        print('Сумма обновлена и комиссия убрана в файле: ', file_name)
        print('------------------------------------------------------------------')


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
                row['Комісія'] = ''

                """Убираем ненужные поля"""
                del row['ID']
                del row['ОписПомилки']
                del row['КодАвторизації']

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
                    if row['Сума'] == '384,00':
                        row['Коментар'] = COMMENTS[row['Компанія']][1]
                    else:
                        row['Коментар'] = COMMENTS[row['Компанія']][0]
                else:
                    row['Коментар'] = COMMENTS[row['Компанія']]

                """Вводим сумму комиссии и суммируем её к оплате"""
                print('Данные оплаты: ')
                pprint.pprint(row)
                commission = input('Комиссии платежа через точку (например 10.01): ')
                row['Сума'] = re.sub(r'(\d)\s+(\d)', r'\1\2', row['Сума'])
                row['Сума'] = re.sub(r'(\d),(\d)', r'\1.\2', row['Сума'])
                row['Сума'] = float(row['Сума']) + float(commission)
                row['Сума'] = "%.2f" % row['Сума']
                row['Сплачено'] = row['Сума']
                print('------------------------------------------------------------------')
                print('Внесенные изменения: ')
                pprint.pprint(row)
                print('------------------------------------------------------------------')

                my_list.append(row)

    """Добавляем изменения в файл, указанный в переменной add_to_file_name"""
    with open(add_to_file_name, encoding='cp1251', mode='a') as output_file:
        fieldnames = ['Дата', 'Коментар', 'Компанія', 'Опис', 'Сума', 'Сплачено', 'Статус', 'Дата_сплати', 'Комісія']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
        writer.writerows(my_list)
        print('------------------------------------------------------------------')
        print('Новые данные добавлены в файл: ', add_to_file_name)
        print('------------------------------------------------------------------')


def main():
    add_commission_to_portmone_csv_file(main_file_name)
    reformat_portmone_csv_file(csv_file_to_reformat, main_file_name)


main_file_name = '2020_07_31_report_1.csv'
csv_file_to_reformat = '2020_07_31_report_2.csv'


COMMENTS = {
    'ТОВ СКІФ КИЇВ ЮА': 'Шота Руставелі 44, 6 — [Office44S6]',

    'Megogo: Максимальная': [
        'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]',
        'Шота Руставелі 44, 5 — [KV249, KV113]',
        'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]',
        'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]',
        'Басейна 17, 32 - [KV521, KV522, KV523, KV524, KV525, KV526, KV527, KV528]'],

    'ФОП Цитович Олег Вадимович': [
        'Кловскьий Спуск 7, 191 — [KV911, KV912, KV913, KV914, KV915]',
        'Кловський Спуск 7, 195 — [KV951, KV952, KV953, KV954, KV955]',
        'Кловскьий Спуск 7, 191 — [KV911, KV912, KV913, KV914, KV915]',
        'Кловський Спуск 7, 195 — [KV951, KV952, KV953, KV954, KV955]'],

    'ТОВ В.О.К.С.': 'Басейна 19, 14  — [Office19B14]',

    'ПАТ ДАТАГРУП': [
        'Шота Руставелі 44, 4 — [KV541, KV542, KV543, KV544]',
        'Шота Руставелі 44, 40 — [KV151, KV152, KV153, KV154]'],
}

if __name__ == '__main__':
    main()