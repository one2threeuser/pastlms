# phishingtool/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.send_phishing_email, name='phishing_simulation'),
]
