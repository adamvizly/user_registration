# Generated by Django 2.2.5 on 2019-09-26 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20190926_0634'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ip_banned',
            field=models.BooleanField(default=False),
        ),
    ]
