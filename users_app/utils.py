import os
import random
import string
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.template.loader import get_template

from dotenv import load_dotenv
load_dotenv()

# from celery import shared_task

from rest_framework_simplejwt.tokens import RefreshToken



def registration_error_message(serializer):

    serializer_errors = serializer.errors
    for field_name, field_errors in serializer_errors.items():
        pass
    return {'message': field_errors}



def error_message(serializer):
    if type(serializer.errors['error']) == type([]):
        serializer_errors = serializer.errors
        for field_name, field_errors in serializer_errors.items():
            pass
        return {'message': field_errors[0]}

    return {'message': serializer.errors}


def generate_otp(length=int(os.environ.get('OTP_LENGHT'))):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    print(f"Generated OTP: {otp}")  # Debugging statement
    return otp


# @shared_task
# async def send_otp_email(email, otp):
def send_otp_email(email, otp):
    # time.sleep(10)
    subject = 'OTP Verification Code'
    from_email = os.environ.get('EMAIL_CONTACT')
    domain = os.environ.get('BACKEND_DOMAIN')
    # OTP_VALIDATION_TIME = os.environ.get('OTP_VALIDATION_TIME')
    logo = f'{domain}/media/logo/introchat.svg'
    context = {'email': email, 'opt': otp, 'logo': logo}
    template = get_template('otp/otp_email_template.html').render(context)
    return send_mail(
        subject,
        None, # Pass None because it's a HTML mail
        from_email,
        [email],
        fail_silently=False,
        html_message = template
    )

def expired_time():
    now = datetime.today()
    result = now + timedelta(minutes=int(os.environ.get('OTP_VALIDATION_TIME')))
    return result


def google_login_response_data(user):
    data = {}
    refresh = RefreshToken.for_user(user)
    data['access'] = str(refresh.access_token)
    data['refresh'] = str(refresh)

    return data

