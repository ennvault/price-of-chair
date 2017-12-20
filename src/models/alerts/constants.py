__author__ = 'jslvtr'
import os


URL = os.environ.get('MAILGUN_URL')
API_KEY = os.environ.get('MAILGUN_API_KEY')
FROM = os.environ.get('MAILGUN_ADDRESS')
ALERT_TIMEOUT = 10
COLLECTION = "alerts"