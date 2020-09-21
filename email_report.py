import datetime
import locale
import smtplib
from pathlib import Path
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
FIRST_DAY_OF_MONTH = datetime.datetime.today().replace(day=1)
LAST_MONTH = (FIRST_DAY_OF_MONTH - datetime.timedelta(days=1)).strftime('%B %Y')
CONFIG_PATH = Path('email_config.ini')

def send_email_report(portmone_small_sum, cashless_sum, total_sum, file_name):
    if CONFIG_PATH.exists():
        cfg = ConfigParser()
        cfg.read(CONFIG_PATH)
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
    msg['Subject'] = Header(f'PGH - абонплата - {LAST_MONTH.title()}', 'cp1251')

    body_text = f'Всем доброго времени суток!<br>' \
                f'Высылаю табличку абонплаты {LAST_MONTH.title()}<br><br>' \
                f'Portmone small: {portmone_small_sum} грн<br>' \
                f'Безналичные оплаты: {cashless_sum} грн<br>' \
                f'Итого: <strong>{total_sum}</strong> грн'

    msg.attach(MIMEText(body_text, 'html', 'cp1251'))

    part = MIMEApplication(file_name.read_bytes(), Name=file_name.name)
    part['Content-Disposition'] = f'attachment; filename="{file_name.name}"'
    msg.attach(part)

    server = smtplib.SMTP_SSL(host, 465)
    server.ehlo()
    server.login(user=from_addr, password=password)
    server.sendmail(from_addr, [to_emails, bcc_email], msg.as_string())
    server.quit()