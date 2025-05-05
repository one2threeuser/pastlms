from django import forms
from .models import PhishingEmailTemplate, RedirectPage



class PhishingEmailTemplateForm(forms.ModelForm):
    class Meta:
        model = PhishingEmailTemplate
        fields = ['sender_name', 'subject', 'body', 'redirect_page', 'attachment']
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'sender_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6, 
                'placeholder': "Enter your email content here... \n\nYou can use code '{username}' for adding username and DO NOT FORGET TO ADD '{link}' for redirect page link"
                }),
            'redirect_page': forms.Select(attrs={'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class RedirectPageForm(forms.ModelForm):
    class Meta:
        model = RedirectPage
        fields = ['name', 'html_content', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'html_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
