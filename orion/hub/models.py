from django.db import models


class Hub(models.Model):
    title = models.CharField(max_length=64, verbose_name='Название')
    alias = models.CharField(max_length=64)
    sort_order = models.IntegerField(verbose_name='порядок сортировки')

    def __str__(self):
        return self.title
