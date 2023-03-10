# Generated by Django 4.0.4 on 2022-08-21 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_alter_group_current_teacher'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manager', models.CharField(max_length=255, verbose_name='actor')),
                ('description', models.TextField(verbose_name='description')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='comment')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_histories', to='main.group')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='histories', to='main.student')),
            ],
            options={
                'verbose_name': 'history',
                'verbose_name_plural': 'histories',
                'ordering': ('-created_at',),
            },
        ),
    ]
