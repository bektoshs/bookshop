from django.core.celery import app
import datetime
from django.core.mail import send_mail
from django.conf import settings

from user.models import User

@app.task(name='send mail')
def send_mail():
    try:
        time_schedule = datetime.now() - datetime.timedelta(hours=1)

        user_objs = User.objects.filter(paid_books=True, created_at=time_schedule)

        for user_obj in user_objs:
            subject = "Mail is about buying"
            message = "Thanks"
            email_form = settings.EMAIL_HOST_USER
            recipient_list = [user_obj.mail]
            send_mail(subject, message, email_form, recipient_list)

    except Exception as e:
        print(e)


