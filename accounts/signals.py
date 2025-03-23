from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .utils import (
    generate_student_credentials,
    generate_lecturer_credentials,
    send_new_account_email,
    generate_password,
)


@receiver(post_save, sender=User)
def post_save_account_receiver(sender, instance=None, created=False, **kwargs):
    """
    Generate student/lecturer credentials only, no automatic email sending.
    """
    if created:
        if instance.is_student:
            username, password = generate_student_credentials()
        elif instance.is_lecturer:
            username, password = generate_lecturer_credentials()

        instance.username = username
        instance.set_password(password)
        instance.is_active = False  #Make user inactive upon creation
        instance.save()  # Save credentials but DO NOT send an email automatically


# AUTOMATIC SENT EMAIL ONCE CREATED
# def post_save_account_receiver(sender, instance=None, created=False, *args, **kwargs):
#     """
#     Send email notification
#     """
#     if created:
#         if instance.is_student:
#             username, password = generate_student_credentials()
#             instance.username = username
#             instance.set_password(password)
#             instance.save()
#             # Send email with the generated credentials
#             send_new_account_email(instance, password)


#         if instance.is_lecturer:
#             username, password = generate_lecturer_credentials()
#             instance.username = username
#             instance.set_password(password)
#             instance.save()
#             # Send email with the generated credentials
#             send_new_account_email(instance, password)



