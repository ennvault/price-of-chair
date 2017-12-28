import datetime
import threading
import time
from flask import Flask, render_template
from src.common.database import Database
from src.models.alerts.alert import Alert


class Background_job(threading.Thread):
    def __init__(self,alert_id):
        threading.Thread.__init__(self)
        self.alert_id = alert_id

    def run(self):
        Database.initialize()
        while Alert.find_by_id(self.alert_id).active == True:
            Alert.turn_email_notification_on(self.alert_id)


def start_thread(alert_id):
    t1 = Background_job(alert_id)
    t1.start()


