# Generated by Django 4.1.2 on 2022-10-25 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_remove_customquestion_heading'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_custom',
            field=models.BooleanField(default=False),
        ),
    ]
