from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from users.models import User


class Complaint(models.Model):

    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return f'{self.user.name} {self.text[:15]}'
