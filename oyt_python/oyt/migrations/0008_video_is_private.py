# Generated by Django 3.2 on 2021-04-10 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyt', '0007_auto_20210408_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='is_private',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]