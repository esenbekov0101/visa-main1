# Generated by Django 4.0.4 on 2022-06-29 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_user_inn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='inn',
            field=models.CharField(max_length=14, unique=True, verbose_name='inn'),
        ),
    ]
