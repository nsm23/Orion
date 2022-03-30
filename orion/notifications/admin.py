from django.contrib import admin
from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'content_type',
        'object_id',
        'content_object',
    )
    list_display_links = ('object_id',)
