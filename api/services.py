import os
from twilio.rest import Client as TwilioClient


class SmsClient(object):
    def __init__(self):
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.client = TwilioClient(account_sid, auth_token)

    def send_sms(self, phone_number):
        return self.client.messages.create(
            body="Visit https://example.com/SUPER_SECRET_CODE",
            from_='+13522689986',
            to=phone_number
        )
