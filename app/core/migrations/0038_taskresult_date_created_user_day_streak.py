# Generated by Django 4.1.3 on 2022-11-25 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_rename_data1_answerfourchoice_correct_option_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskresult',
            name='date_created',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='user',
            name='day_streak',
            field=models.IntegerField(default=0),
        ),
    ]
