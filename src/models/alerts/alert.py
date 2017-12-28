import uuid
import datetime
import requests
from src.common.database import Database
import src.models.alerts.constants as AlertConstants
from src.models.items.item import Item

__author__ = 'ennvault'


class Alert(object):
    def __init__(self, user_email, price_limit, item_id, active=True, email_count = 0, email_alert = False, last_checked=None, _id=None):
        self.user_email = user_email
        self.price_limit = price_limit
        self.active = active
        self.item = Item.get_by_id(item_id)
        self.last_checked = datetime.datetime.now() if last_checked is None else last_checked
        self._id = uuid.uuid4().hex if _id is None else _id
        self.email_alert = email_alert
        self.email_count = email_count

    def __repr__(self):
        return "<Alert for {} on item {} with price {}>".format(self.user_email, self.item.name, self.price_limit)


    def send(self):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart('mixed')
        msg['From'] = AlertConstants.FROM
        msg['To'] = self.user_email
        msg['Subject'] = ("Price limit reached for {} ").format(self.item.name)
        textpart = MIMEText(
            ("we have found a deal! ({}). To navigate to the alert page, visit {}".format(self.item.url,
                                                                                         "https://price-alert-ennvault.herokuapp.com".format(
                                                                                             self._id))), 'plain')

        msg.attach(textpart)
        smtp = smtplib.SMTP(AlertConstants.SMTP_HOSTNAME, AlertConstants.SMTP_PORT)
        smtp.login(AlertConstants.SMTP_EMAIL, AlertConstants.SMTP_PASSWORD)
        smtp.sendmail(AlertConstants.FROM, self.user_email, msg.as_string())



    @classmethod
    def find_needing_update(cls, minutes_since_update=AlertConstants.ALERT_TIMEOUT):
        last_updated_limit = datetime.datetime.now() - datetime.timedelta(minutes=minutes_since_update)
        return [cls(**elem) for elem in Database.find(AlertConstants.COLLECTION,
                                                      {"last_checked":
                                                           {"$lte": last_updated_limit},
                                                  "active": True
                                                       })]

    def save_to_mongo(self):
        Database.update(AlertConstants.COLLECTION, {"_id": self._id}, self.json())

    def json(self):
        return {
            "_id": self._id,
            "price_limit": self.price_limit,
            "last_checked": self.last_checked,
            "user_email": self.user_email,
            "item_id": self.item._id,
            "active": self.active,
            "email_alert":self.email_alert,
            "email_count": self.email_count
        }


    def load_item_price(self):
        self.item.load_price()
        self.last_checked = datetime.datetime.now()
        self.item.save_to_mongo()
        self.save_to_mongo()

        return self.item.price

    def send_email_if_price_reached(self):
        print("item price", self.item.price, "price limit", self.price_limit)
        if self.price_limit < self.item.price:
            if self.email_count <= 3 :
                self.send()
                print("email sent")


    @classmethod
    def find_by_user_email(cls, user_email):
        return [cls(**elem) for elem in Database.find(AlertConstants.COLLECTION, {'user_email': user_email})]

    @classmethod
    def find_by_id(cls, alert_id):
        return cls(**Database.find_one(AlertConstants.COLLECTION, {'_id': alert_id}))

    def deactivate(self):
        self.active = False
        self.save_to_mongo()

    def activate(self):
        self.active = True
        self.save_to_mongo()

    def delete(self):
        Database.remove(AlertConstants.COLLECTION, {'_id': self._id})

    @staticmethod
    def check_for_update(alert_id):
        Database.initialize()
        alert = Alert.find_by_id(alert_id)
        print("got alert id ")
        if alert.active == True and alert.email_alert == True:
            # print("alert is active and checking")
            alert.load_item_price()
            print(alert.load_item_price())
            alert.send_email_if_price_reached()
        else:
            print("alert has been deactivated ")
            quit()


    def email_alert_on(self):
        self.email_alert = True
        self.save_to_mongo()

    def email_alert_off(self):
        self.email_alert = False
        self.save_to_mongo()


    @classmethod
    def turn_email_notification_on(cls,alert_id):
        alert = Alert.find_by_id(alert_id)
        alert.email_alert_on()
        while True:
            time = datetime.datetime.now()
            print(time.strftime("%d-%m-%Y %H:%M:%S"))
            Alert.check_for_update(alert_id)
            sleep(43200)

