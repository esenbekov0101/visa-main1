# Generated by Django 4.0.4 on 2022-08-29 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_teacherhistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='students',
            field=models.ManyToManyField(related_name='groups', to='main.student'),
        ),
        migrations.AddField(
            model_name='group',
            name='students',
            field=models.ManyToManyField(related_name='groups', to='main.student'),
        ),
        migrations.DeleteModel(
            name='GroupStudent',
        ),
    ]
