# Generated by Django 4.1.1 on 2022-09-26 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_question_left_choice_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choice',
            old_name='left_side',
            new_name='side',
        ),
    ]