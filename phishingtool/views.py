# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import PhishingEmailTemplate, EmailActivity, PhishingSubmission
from accounts.models import User, Student
from django.contrib import messages

# NEW
from django.http import HttpResponse, FileResponse, Http404
from django.utils.html import strip_tags
from django.urls import reverse
from django.utils.timezone import now
from .forms import PhishingEmailTemplateForm, RedirectPageForm
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required, lecturer_required, student_required
from django.core.mail import EmailMultiAlternatives
import mimetypes
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import os

@login_required
@admin_required
def send_phishing_email(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        template_id = request.POST.get('template_id')
        user = User.objects.get(id=user_id)
        template = PhishingEmailTemplate.objects.get(id=template_id)

        # Create the activity log
        email_log = EmailActivity.objects.create(user=user, template=template)

        # Build tracking links
        open_url = request.build_absolute_uri(reverse('track_open', args=[email_log.id]))
        # open_url = f"http://mydomain.site/phishing-tool/track/open/{email_log.id}/"
        click_url = request.build_absolute_uri(reverse('track_click', args=[email_log.id]))
        report_url = request.build_absolute_uri(reverse('track_report', args=[email_log.id]))
        attachment_url = request.build_absolute_uri(reverse('track_attachment_download', args=[email_log.id]))


        # Use template.link_url if provided, else fallback to tracking
        # click_url = request.build_absolute_uri(reverse('track_click', args=[email_log.id]))

        subject = template.subject
        html_body = template.body.format(
            username=user.username,
            firstname=user.first_name,
            lastname=user.last_name,
            email=user.email,
            link=click_url,
            report=report_url,
            attachment=attachment_url,
            current_time=timezone.now().strftime('%A, %d %B %Y at %I:%M %p')
        )

        from_email = f"{template.sender_name} <{template.sender_email}>"


        # Add tracking pixel + report link
        # if template.attachment:
        #     html_body += f'<p><a href="{attachment_url}">View and Download Attachment</a></p>'

        html_body += f"""
            <img src="{open_url}" width="1" height="1" style="display:none;" alt="tracker">
        """
        text_body = strip_tags(html_body)

        # Send the email with optional attachment
        email = EmailMultiAlternatives(subject, text_body, from_email, [user.email])
        email.attach_alternative(html_body, "text/html")

        if template.attachment:
            file_path = template.attachment.path
            content_type, _ = mimetypes.guess_type(file_path)

            email.attach(
                filename=template.attachment.name,
                content=template.attachment.read(),
                mimetype=content_type or 'application/octet-stream'
            )

        email.send()

        messages.success(request, f"Email has been sent to {user.username}.")

    users = User.objects.all()
    templates = PhishingEmailTemplate.objects.all()
    logs = EmailActivity.objects.select_related('user', 'template').order_by('-sent_at')

    return render(request, 'core/phishing_simulation.html', {
        'users': users,
        'templates': templates,
        'logs': logs
    })


# TRACKING
def track_open(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)

    # print(f"Tracking pixel loaded for email ID {pk}")

    if not log.opened:
        log.opened = True
        log.open_time = now()
        log.save()
    # return 1x1 transparent gif
    return HttpResponse(
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B',
        content_type='image/gif'
    )

def track_click(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)

    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

    # Skip logging if request likely came from a bot/crawler
    known_bots = ['microsoft', 'defender', 'urlscan', 'bot', 'crawler']
    if not any(bot in user_agent for bot in known_bots):
        if not log.clicked:
            log.clicked = True
            log.click_time = now()

        # if not log.opened:
        #     log.opened = True
        #     log.open_time = now()

        log.save()

    return redirect('phishing_redirect', pk=pk)

def track_report(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)
    if not log.reported:
        log.reported = True
        log.report_time = now()
        log.save()

    # if not log.opened:
    #     log.opened = True
    #     log.open_time = now()
    #     log.save()

    return render(request, 'phishingtool/redirect_temp/default_page.html', {'log': log})

def track_attachment_download(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)
    template = log.template

    if not log.clicked:
        log.clicked = True
        log.click_time = now()

    if not log.opened:
        log.opened = True
        log.open_time = now()

    if not log.attachment_downloaded:
        log.attachment_downloaded = True
        log.attachment_time = now()

    log.save()

    # Serve the attachment
    if template and template.attachment:
        return FileResponse(template.attachment.open(), as_attachment=True, filename=template.attachment.name)

    return HttpResponse("No attachment available.", status=404)

def track_redirect_file_download(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)
    redirect_page = log.template.redirect_page

    # Log the download
    log.clicked = True
    log.attachment_downloaded = True
    log.attachment_time = now()
    log.save()

    if redirect_page.file:
        file_path = redirect_page.file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))

    raise Http404("File not found.")



@csrf_exempt
def phishing_login_capture(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Save the fake credentials
        PhishingSubmission.objects.create(
            activity=log,
            email=email,
            password=password
        )

        # Update activity log
        log.submitted_data = True
        log.submission_time = now()

        if not log.clicked:
            log.clicked = True
            log.click_time = now()

        log.save()

        return render(request, 'phishingtool/redirect_temp/default_page.html')

    return HttpResponse("Invalid request", status=400)


# Redirect Page (displays custom HTML)
def phishing_redirect_page(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)
    redirect_page = log.template.redirect_page

    if redirect_page and redirect_page.html_content:
        html = redirect_page.html_content

        # Replace any custom placeholders
        capture_url = reverse('phishing_login_capture', args=[log.id])
        html = html.replace('__CAPTURE_URL__', capture_url)

        # Handle uploaded file URL
        if redirect_page.file:
            file_download_url = reverse('track_redirect_file_download', args=[log.id])
            html = html.replace('__REDIRECT_FILE__', file_download_url)

        return HttpResponse(html)

    # If no redirect page or HTML content found
    return render(request, 'phishingtool/redirect_temp/default_page.html', {'log': log})





def add_redirect_page(request):
    if request.method == 'POST':
        form = RedirectPageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Redirect page created successfully.")
            return redirect('add_template')  # or wherever your template creation is
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RedirectPageForm()

    return render(request, 'phishingtool/add_redirect_page.html', {'form': form})



@login_required
@admin_required
def phishing_dashboard(request):
    logs = EmailActivity.objects.select_related('user', 'template').order_by('-sent_at')
    return render(request, 'core/phishing_simulation.html', {'logs': logs})

@login_required
@admin_required
def add_template(request):
    if request.method == 'POST':
        form = PhishingEmailTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Phishing template created successfully.")
            # return redirect('phishing_dashboard')
        else:
            messages.error(request, "There was an errors.")
    else:
        form = PhishingEmailTemplateForm()

    return render(request, 'phishingtool/add_template.html', {'form': form})


def delete_email_activity(request, pk):
    log = get_object_or_404(EmailActivity, pk=pk)
    log.delete()
    messages.success(request, "Email log deleted successfully.")
    return redirect('phishing_dashboard')