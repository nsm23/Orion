# Generated by Django 4.0.2 on 2022-03-18 13:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='rating',
            field=models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MinValueValidator(limit_value=1, message='The value must be between 1 and 10.'), django.core.validators.MaxValueValidator(limit_value=10, message='The value must be between 1 and 10.')], verbose_name='Rating'),
        ),
    ]
