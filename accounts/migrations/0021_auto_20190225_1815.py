# Generated by Django 2.1.1 on 2019-02-25 09:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_auto_20190225_1810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='following',
            field=models.ManyToManyField(blank=True, default='admin', related_name='followed_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
