# Generated by Django 3.0.8 on 2020-08-19 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0012_auto_20200814_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertag',
            name='validFlg',
            field=models.SmallIntegerField(default=1),
        ),
    ]
