# Generated by Django 3.0.8 on 2020-07-31 06:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0012_works_wordstranslated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='translationhistory',
            name='beforeTranslationWithTags',
        ),
    ]
