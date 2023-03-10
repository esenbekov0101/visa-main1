# Generated by Django 4.0.4 on 2022-09-03 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_alter_group_students_delete_groupstudent'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='is archived'),
        ),
        migrations.AlterField(
            model_name='history',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='histories', to='main.student'),
        ),
    ]
