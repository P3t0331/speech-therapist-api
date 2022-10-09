# Generated by Django 4.1.1 on 2022-10-08 12:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_basicchoice_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basicchoice',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]