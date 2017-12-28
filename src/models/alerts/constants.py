__author__ = 'ennvault'
import os


URL = os.environ.get('MAILGUN_URL')
API_KEY = os.environ.get('MAILGUN_API_KEY')
FROM = os.environ.get('MAILGUN_ADDRESS')
ALERT_TIMEOUT = 10
COLLECTION = "alerts"
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SMTP_HOSTNAME = os.environ.get('SMTP_HOSTNAME')
SMTP_PORT = os.environ.get('SMTP_PORT')
SMTP_EMAIL = os.environ.get('SMTP_EMAIL')