from django.db import models

# NEW
from accounts.models import User

# Create your models here.

class RedirectPage(models.Model):
    name = models.CharField(max_length=255)
    html_content = models.TextField()
    file = models.FileField(upload_to='redirect_files/', blank=True, null=True)


    def __str__(self):
        return self.name


class PhishingEmailTemplate(models.Model):
    sender_name = models.CharField(max_length=255, default='PAST')
    sender_email = models.EmailField(default='past.bn@gmail.com')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    link_url = models.URLField(blank=True, null=True)
    redirect_page = models.ForeignKey(RedirectPage, on_delete=models.SET_NULL, null=True, blank=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # redirect_html = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.subject
    


# NEW: Track Email Activity
class EmailActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey('PhishingEmailTemplate', on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    opened = models.BooleanField(default=False)
    open_time = models.DateTimeField(null=True, blank=True)

    clicked = models.BooleanField(default=False)
    click_time = models.DateTimeField(null=True, blank=True)

    reported = models.BooleanField(default=False)
    report_time = models.DateTimeField(null=True, blank=True)

    attachment_downloaded = models.BooleanField(default=False)
    attachment_time = models.DateTimeField(null=True, blank=True)

    submitted_data = models.BooleanField(default=False)
    submission_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.template.subject}"



class PhishingSubmission(models.Model):
    activity = models.ForeignKey(EmailActivity, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)



