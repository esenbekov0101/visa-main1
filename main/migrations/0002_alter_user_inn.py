# Generated by Django 4.0.4 on 2022-06-29 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='inn',
            field=models.PositiveBigIntegerField(unique=True, verbose_name='inn'),
        ),
    ]
