# Generated by Django 2.1.1 on 2019-02-28 05:00

from django.db import migrations, models
import tweets.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0013_auto_20190225_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tsubuyaki',
            name='title',
            field=models.CharField(default='No title', max_length=120, validators=[tweets.validators.validate_content]),
        ),
    ]