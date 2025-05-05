# phishingtool/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.send_phishing_email, name='phishing_simulation'),
    
    # NEW
    path('track/open/<int:pk>/', views.track_open, name='track_open'),
    path('track/click/<int:pk>/', views.track_click, name='track_click'),
    path('track/report/<int:pk>/', views.track_report, name='track_report'),
    path('', views.phishing_dashboard, name='phishing_dashboard'),

    path('template/add/', views.add_template, name='add_template'),
    path('redirect/<int:pk>/', views.phishing_redirect_page, name='phishing_redirect'),
    # path('template/<int:pk>/add-redirect/', views.add_redirect_page, name='add_redirect_page'),
    path('redirect/add/', views.add_redirect_page, name='add_redirect_page'),
    path('track/attachment/<int:pk>/', views.track_attachment_download, name='track_attachment_download'),
    path('capture/<int:pk>/', views.phishing_login_capture, name='phishing_login_capture'),
    path('redirect-file/<int:pk>/', views.track_redirect_file_download, name='track_redirect_file_download'),
    path('email-activity/<int:pk>/delete/', views.delete_email_activity, name='delete_email_activity'),


]
