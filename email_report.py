import os
import datetime
import locale
import smtplib
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
TODAY = datetime.datetime.today()
FIRST = TODAY.replace(day=1)
LAST_MONTH = (FIRST - datetime.timedelta(days=1)).strftime('%B %Y')

def send_email_report(portmone_small_sum, cashless_sum, total_sum, file_name):
    if os.path.exists('email_config.ini'):
        cfg = ConfigParser()
        cfg.read('email_config.ini')
    else:
        print("Файл конфигурации email_config.ini не найден!")
        raise SystemExit

    host = cfg.get("smtp", "host")
    from_addr = cfg.get("smtp", "from_addr")
    password = cfg.get("smtp", "password")
    to_emails = cfg.get("smtp", "to_addreses")
    bcc_email = cfg.get("smtp", "bcc_addr")

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_emails
    msg['Subject'] = Header(f'PGH - абонплата - {LAST_MONTH}', 'cp1251')

    body_text = f'Всем доброго времени суток!\n' \
                f'Высылаю табличку абонплаты {LAST_MONTH}\n' \
                f'Portmone small: {portmone_small_sum} грн\n' \
                f'Безналичные оплаты: {cashless_sum} грн\n' \
                f'Итого: {total_sum} грн'

    msg.attach(MIMEText(body_text, 'plain', 'cp1251'))

    with open(file_name, "rb") as open_file:
        part = MIMEApplication(open_file.read(), Name=os.path.basename(file_name))
    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
    msg.attach(part)

    server = smtplib.SMTP_SSL(host, 465)
    server.ehlo()
    server.login(user=from_addr, password=password)
    server.sendmail(from_addr, [to_emails, bcc_email], msg.as_string())
    server.quit()