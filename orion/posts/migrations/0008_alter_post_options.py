# Generated by Django 4.0.2 on 2022-02-23 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_post_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created_at',)},
        ),
    ]
