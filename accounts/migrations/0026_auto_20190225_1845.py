# Generated by Django 2.1.1 on 2019-02-25 09:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_auto_20190225_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='following',
            field=models.ManyToManyField(blank=True, default='(<User: admin>, False)', related_name='followed_by', to=settings.AUTH_USER_MODEL),
        ),
    ]