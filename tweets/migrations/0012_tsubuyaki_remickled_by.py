# Generated by Django 2.1.1 on 2019-02-19 12:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tweets', '0011_auto_20190206_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='tsubuyaki',
            name='remickled_by',
            field=models.ManyToManyField(blank=True, related_name='remickled', to=settings.AUTH_USER_MODEL),
        ),
    ]
