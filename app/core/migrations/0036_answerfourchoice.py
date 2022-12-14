# Generated by Django 4.1.2 on 2022-11-15 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_alter_task_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerFourChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data1', models.CharField(max_length=255)),
                ('data2', models.CharField(max_length=255)),
                ('data3', models.CharField(max_length=255)),
                ('data4', models.CharField(max_length=255)),
                ('data5', models.CharField(max_length=255)),
                ('chosen_option', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=True)),
                ('assigned_to_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_fourchoice', to='core.questionconnectimageanswer')),
            ],
        ),
    ]
