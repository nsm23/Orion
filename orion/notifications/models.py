from __future__ import annotations
from typing import List

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from users.models import User


class Notification(models.Model):

    class NotificationStatus(models.TextChoices):
        UNREAD = 'UNREAD', _('UNREAD'),
        READ = 'READ', _('READ'),

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    status = models.CharField(max_length=8, choices=NotificationStatus.choices, default=NotificationStatus.UNREAD)
    user = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='notifications_author',
    )
    target_user = models.ForeignKey(
        User,
        verbose_name='Адресат',
        on_delete=models.CASCADE,
        related_name='notifications_target',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'notification of {self.content_object} {self.object_id}'

    @staticmethod
    def create_notification(content_type, object_id, user_id, target_user_id):
        notification = Notification(
            content_type=content_type,
            object_id=object_id,
            status=Notification.NotificationStatus.UNREAD,
            user_id=user_id,
            target_user_id=target_user_id
        )
        notification.save()

    @staticmethod
    def delete_notification(content_type, object_id):
        notification = Notification.objects.get(content_type=content_type, object_id=object_id)
        notification.delete()

    @staticmethod
    def mark_notifications_read(notifications: List[Notification]):
        for notification in notifications:
            notification.status = Notification.NotificationStatus.READ
        Notification.objects.bulk_update(notifications, ['status'])
