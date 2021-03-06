# Generated by Django 4.0.2 on 2022-03-27 18:43

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0004_alter_taggeditem_content_type_alter_taggeditem_tag'),
        ('posts', '0009_alter_post_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(max_length=200, verbose_name='Элиас для урла'),
        ),
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'DRAFT'), ('ACTIVE', 'ACTIVE'), ('ON MODERATION', 'ON MODERATION'), ('DECLINED', 'DECLINED'), ('DELETED', 'DELETED'), ('BANNED', 'BANNED')], default='ACTIVE', max_length=16),
        ),
    ]
