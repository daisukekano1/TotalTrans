# Generated by Django 3.0.8 on 2020-07-31 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0013_remove_translationhistory_beforetranslationwithtags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translationhistory',
            name='TranslationType',
            field=models.CharField(max_length=10, null=True),
        ),
    ]