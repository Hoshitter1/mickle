# Generated by Django 2.1.1 on 2019-02-06 06:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tweets', '0009_auto_20190130_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='tsubuyaki',
            name='purchased_by',
            field=models.ManyToManyField(blank=True, related_name='purchased_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
