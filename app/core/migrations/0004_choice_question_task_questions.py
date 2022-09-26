# Generated by Django 4.1.1 on 2022-09-26 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_task'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=255)),
                ('left_side', models.BooleanField(default=True)),
                ('assigned_to_identifier', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('left_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='left_choice', to='core.choice')),
                ('right_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='right_choice', to='core.choice')),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='questions',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.question'),
        ),
    ]