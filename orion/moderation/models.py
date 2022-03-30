from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from users.models import User


class Moderation(models.Model):
    class ModerationDecision(models.TextChoices):
        NONE = 'NONE', 'None'
        APPROVE = 'APPROVE', 'Approve'
        DECLINE = 'DECLINE', 'Decline'
        BAN = 'BAN', 'Ban'
        UNBAN = 'UNBAN', 'Unban'

    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='moderation_actions',
        null=True,
        blank=True,
    )
    date = models.DateTimeField(
        auto_now=True,
    )
    decision = models.CharField(
        choices=ModerationDecision.choices,
        max_length=16,
    )
    comment = models.CharField(
        max_length=256,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
