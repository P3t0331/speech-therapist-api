# Generated by Django 4.1.1 on 2022-10-08 11:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_tag_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='basicchoice',
            name='created_by',
            field=models.ForeignKey(default=21, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
