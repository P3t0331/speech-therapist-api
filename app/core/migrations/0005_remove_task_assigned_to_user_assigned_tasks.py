# Generated by Django 4.1.2 on 2022-10-12 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_task_created_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='assigned_to',
        ),
        migrations.AddField(
            model_name='user',
            name='assigned_tasks',
            field=models.ManyToManyField(to='core.task'),
        ),
    ]
