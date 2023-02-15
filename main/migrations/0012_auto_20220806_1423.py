# Generated by Django 4.0.4 on 2022-08-06 14:23

from django.db import migrations


def delete_all_lessons(apps, schema_editor):
    Lesson = apps.get_model('main', 'Lesson')
    Lesson.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_teacher'),
    ]

    operations = [
        migrations.RunPython(delete_all_lessons),
    ]
