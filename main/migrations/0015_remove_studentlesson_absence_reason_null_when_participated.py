# Generated by Django 4.0.4 on 2022-08-06 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_studentlesson_has_participated_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='studentlesson',
            name='absence_reason_null_when_participated',
        ),
    ]
