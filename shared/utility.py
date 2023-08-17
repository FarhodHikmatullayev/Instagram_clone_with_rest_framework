import re
import threading

import phonenumbers
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from decouple import config
from twilio.rest import Client

regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
regex_phone = re.compile(r'^[+]998([0-9][012345789]|[0-9][125679]|7[01234569])[0-9]{7}$')
regex_username = re.compile(r'^[a-zA-Z0-9_.-]+$')


def check_email_or_phone(email_phone_number):
    try:
        parse_number = phonenumbers.parse(email_phone_number)
        if phonenumbers.is_valid_number(parse_number):
            email_phone_number = 'phone'
    except phonenumbers.NumberParseException:
        if re.fullmatch(regex_email, email_phone_number):
            email_phone_number = 'email'
        else:
            email_phone_number = 'error'
    # if re.fullmatch(regex_email, email_phone_number):
    #     email_phone_number = 'email'
    # elif phonenumbers.is_valid_number(phonenumbers.parse(email_phone_number)):
    #     email_phone_number = 'phone'
    # else:
    #     return 'error'
    print('input_type_phone_or_email_or_error', email_phone_number)
    return email_phone_number


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == 'html':
            email.content_subtype = 'html'
            EmailThread(email).start()


def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {'code': code}
    )
    Email.send_email(
        {
            'subject': "Ro'yxatdan o'tish",
            'to_email': email,
            'body': html_content,
            'content_type': "html",
        }
    )


def send_phone_code(phone, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"salom do'stim, sizning tasdiqlash kodingiz : {code}\n",
        from_='+998943932345',
        to=f"{phone}"
    )


def check_user_type(user_input):
    if re.fullmatch(regex_email, user_input):
        user_input = 'email'
    elif re.fullmatch(regex_phone, user_input):
        user_input = 'phone'
    elif re.fullmatch(regex_username, user_input):
        user_input = 'username'
    else:
        data = {
            'status': False,
            'message': 'username, Email yoki telefon raqamingiz noto\'g\'ri'
        }
        raise ValidationError(data)
    return user_input
