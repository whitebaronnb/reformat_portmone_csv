# Программа для обработки файлов .csv от portmone
## Что нужно для работы с скриптом:

1. Создайте папку ```files``` в той же папке что и основной файл ```main.py```. 
2. В папку ```files``` положите два файла ```.csv``` формата и один файл формата ```.xslx```.
Важно чтобы основной файл и файл оплат по реквизитам были с названием ```yyyy_mm_dd_report_1.csv``` и ```yyyy_mm_dd_report_2.csv``` соответственно.
Файл ```.xlsx``` должен начинаться с слова ```абонплата```. 
3. Для отправки email отчетов, в директорию с файлом ```main.py``` положите файл конфигурации вашего почтового ящика 
с названием ```email_config.ini```. Структура файла следующая:
```
[smtp]
host = smtp.example.com 
from_addr = myemail@mail.com 
password = password123
to_addreses = to_address@mail.com 
bcc_addr = bcc_address@mail.com
``` 
4. Создать виртуальное окружение и установить модули из ```requirements.txt```.

5. Запустить файл из виртуального окружения с помощью команды:
```python main.py```
6. После обработки информации, скрипт спросит у вас, отправлять ли ему email отчет?
Для ответа укажите да или нет одной буквой на англ раскладке (y/n).

## Запуск отдельных функций:
- В файле ```main.py``` в функции ```main()``` закоментировать ненужные функции и запустить как в шаге ```5.```
