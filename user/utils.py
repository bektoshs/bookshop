from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import requests
import re

MESSAGE_RP="Bookshop tizimining parolini tiklash kodi: "
MESSAGE_SC="Bookshop tizimiga kirish codi: "
pattern = r'^(\+?998)?([. \-])?((\d){2})([. \-])?(\d){3}([. \-])?(\d){2}([. \-])?(\d){2}$'
email_pattern = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

def validate_phone_number_or_email(value):
    """Custom validation function that checks if phone number follows UZB pattern"""
    if not re.match(pattern, value) or not re.match(email_pattern, value):
        return ValidationError("%(value) does not follow phone number or email pattern",
                               params={'value': value})

def is_email(value):
    if re.match(email_pattern, value):
        return True
    return False

def get_message_payload(phone_number, message="Testing? provide message"):

    payload = {
        'mobile_phone': phone_number,
        'message': message,
    }

    return payload


ESKIZ_AUTH_URL = "http://notify.eskiz.uz/api/auth/login"
def get_token():
    payload = {
        'email': settings.ESKIZ_EMAIL,
        'password': settings.ESKIZ_SECRET_KEY
    }
    try:
        token = requests.post(ESKIZ_AUTH_URL, headers={}, json=payload).json()['data']['token']
    except:
        raise ValueError("Eskiz is not working!")
    return token

def get_header():
    header = {
        'Authorization': 'Bearer {}'.format(get_token()),
        'Content-type': 'application/json'
    }
    return header

def send_code_to_phone_number(code, phone_number, reset=False):
    """Function that send the code to the user's phone number,
    we can use it to reset the password or sign up verification.
    """
    if reset:
        msg = "{} {}".format(MESSAGE_RP, code)
    else:
        msg = "{} {}".format(MESSAGE_SC, code)
    payload = get_message_payload(phone_number, msg)
    headers = get_header()
    res = requests.post(settings.ESKIZ_URL, json=payload, headers=headers)
    return res


# helper functions
def generate_correct_phone_number(phone_num):
    if len(phone_num) <= 12:
        if len(phone_num.split()) == 1:
            return phone_num if len(phone_num) > 9 else '998' + phone_num
        else:
            c_ph_n = ''.join([c for c in phone_num if c.isdigit()])
            return '998' + c_ph_n
    else:
        c_ph_n = ''.join([c for c in phone_num if c.isdigit()])
        return c_ph_n


def is_phone_number_valid(phone_number):
    if not phone_number:
        return False, "Please provide a phone_number or an email!"

    if not re.match(pattern, phone_number) and not re.match(email_pattern, phone_number):
        return False, "Please make sure phone_number, email is correct!"

    return True, phone_number


# User serializer related utils function
def is_status_paid(obj):
    date = str(obj.paid_till).split(' ')[0]
    if obj.paid_till is None:
        return False
    paid_date = datetime.strptime(date, '%Y-%m-%d') + \
        timedelta(hours=23, minutes=59, seconds=59)
    if paid_date < datetime.today():
        return False
    return True
