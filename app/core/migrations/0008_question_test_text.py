# Generated by Django 4.1.1 on 2022-09-26 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_left_side_choice_side'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='test_text',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
