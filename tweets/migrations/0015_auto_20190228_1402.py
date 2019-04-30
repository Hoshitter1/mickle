# Generated by Django 2.1.1 on 2019-02-28 05:02

from django.db import migrations, models
import tweets.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0014_auto_20190228_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tsubuyaki',
            name='content',
            field=models.CharField(max_length=620, validators=[tweets.validators.validate_content]),
        ),
    ]