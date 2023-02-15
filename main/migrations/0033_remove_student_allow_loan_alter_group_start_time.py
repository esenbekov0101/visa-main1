# Generated by Django 4.0.4 on 2022-09-04 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_group_comment_student_comment_user_birth_day_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='allow_loan',
        ),
        migrations.AlterField(
            model_name='group',
            name='start_time',
            field=models.PositiveSmallIntegerField(choices=[(8, '8:00 - 9:00'), (9, '9:00 - 10:00'), (10, '10:00 - 11:00'), (11, '11:00 - 12:00'), (12, '12:00 - 13:00'), (13, '13:00 - 14:00'), (14, '14:00 - 15:00'), (15, '15:00 - 16:00'), (16, '16:00 - 17:00'), (17, '17:00 - 18:00'), (18, '18:00 - 19:00'), (19, '19:00 - 20:00'), (20, '20:00 - 21:00')], verbose_name='start time'),
        ),
    ]
