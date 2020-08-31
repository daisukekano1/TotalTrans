# Generated by Django 3.0.8 on 2020-08-25 02:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0016_delete_person'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGlossary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=100, null=True)),
                ('numberofcount', models.IntegerField(null=True)),
                ('validFlg', models.SmallIntegerField(default=1)),
                ('createdDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'index_together': {('user_id',)},
            },
        ),
    ]
