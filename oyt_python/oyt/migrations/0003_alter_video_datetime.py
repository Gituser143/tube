# Generated by Django 3.2 on 2021-04-08 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyt', '0002_auto_20210408_0734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='datetime',
            field=models.DateField(auto_now=True),
        ),
    ]
