import os
from twilio.rest import Client as TwilioClient
import pyotp


class SmsClient(object):
    def __init__(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.sms_enabled = os.getenv("SMS_ENABLED", "False") == "True"
        self.client = TwilioClient(account_sid, auth_token)

    def send_sms(self, phone_number):
        if (not self.sms_enabled):
            return False

        return self.client.messages.create(
            body="Visit https://example.com/SUPER_SECRET_CODE",
            from_='+13522689986',
            to=phone_number
        )

    def send_sms_magic_link(self, phone_number, magic_link):
        if (not self.sms_enabled):
            print(magic_link)
            return False

        return self.client.messages.create(
            body=f"Visit {magic_link}",
            from_='+13522689986',
            to=phone_number
        )

    def send_sms_access_code(self, phone_number, otp):
        if (not self.sms_enabled):
            return False

        return self.client.messages.create(
            body=f"Enter the access code {otp} in the Insights Agent app",
            from_='+13522689986',
            to=phone_number
        )


class OtpClient(object):
    def verify(self, passcode):
        totp = pyotp.TOTP('base32secret3232', interval=2000)
        return totp.verify(passcode)

    def generate(self):
        totp = pyotp.TOTP('base32secret3232', interval=2000)
        return totp.now()
