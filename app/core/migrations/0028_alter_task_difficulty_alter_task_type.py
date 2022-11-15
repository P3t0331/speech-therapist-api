# Generated by Django 4.1.2 on 2022-11-14 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_alter_task_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='difficulty',
            field=models.CharField(choices=[('EASY', 'Easy'), ('HARD', 'Hard')], max_length=20),
        ),
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.CharField(choices=[('FOUR CHOICES (IMAGE-TEXTS)', 'Four Choices Image'), ('FOUR CHOICES (TEXT-IMAGES)', 'Four Choices Text'), ('CONNECT PAIRS (TEXT-IMAGE)', 'Connect Pairs Text Image'), ('CONNECT PAIRS (IMAGE-TEXT)', 'Connect Pairs Text Text')], max_length=50),
        ),
    ]