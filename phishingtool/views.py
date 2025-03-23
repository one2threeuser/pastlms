# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import PhishingEmailTemplate
from accounts.models import User, Student
from django.contrib import messages

def send_phishing_email(request):
    # instance = User.objects.all()
    # instance = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        template_id = request.POST.get('template_id')
        user = User.objects.get(id=user_id)
        template = PhishingEmailTemplate.objects.get(id=template_id)

        # Customize the email content
        subject = template.subject
        body = template.body.format(username=user.username, link="http://phishing-link.com")

        # full_name = instance.get_full_name
        username = User.objects.get(id=user_id)

        # Send the email
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        messages.success(request, ("Email has been Sent to " + user_id + " is successful."))
        # return redirect('')

    # Fetch all users and templates for the selection form
    users = User.objects.all()
    templates = PhishingEmailTemplate.objects.all()
    return render(request, 'core/phishing_simulation.html', {'users': users, 'templates': templates})
