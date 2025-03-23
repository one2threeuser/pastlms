# views.py
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

def send_test_email(request):
    subject = "Test Email from Django"
    message = "Hello! This is a test email sent from Django."
    recipient_list = ["hakeemkhairulmd@gmail.com"]  # replace with your own test email
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        return HttpResponse("Test email sent successfully!")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
