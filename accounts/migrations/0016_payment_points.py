# Generated by Django 2.1.1 on 2019-02-10 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_auto_20190209_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='points',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
