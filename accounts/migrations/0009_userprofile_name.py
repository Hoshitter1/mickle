# Generated by Django 2.1.1 on 2019-01-31 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20190130_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='name',
            field=models.CharField(default='(´･ω･)', max_length=50),
        ),
    ]