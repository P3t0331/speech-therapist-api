# Generated by Django 4.1.3 on 2022-11-26 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_user_last_result_posted'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='diagnosis',
            field=models.TextField(blank=True),
        ),
    ]
