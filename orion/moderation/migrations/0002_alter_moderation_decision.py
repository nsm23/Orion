from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderation',
            name='decision',
            field=models.CharField(choices=[('NONE', 'None'), ('APPROVE', 'Approve'), ('DECLINE', 'Decline'), ('BAN', 'Ban'), ('UNBAN', 'Unban')], max_length=16),
        ),
    ]
