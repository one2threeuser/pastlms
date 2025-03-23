from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import PhishingEmailTemplate

@admin.register(PhishingEmailTemplate)
class PhishingEmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'updated_at')
    search_fields = ('subject',)