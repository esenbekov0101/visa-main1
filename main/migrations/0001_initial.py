# Generated by Django 4.0.4 on 2022-06-29 10:18

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_better_admin_arrayfield.models.fields
import main.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(message='Phone number must be in the format: 996XXX123456.', regex='^996\\d{9}$')], verbose_name='phone')),
                ('fullname', models.CharField(max_length=255, verbose_name='full name')),
                ('role', models.CharField(choices=[('manager', 'manager'), ('operator', 'operator'), ('owner', 'owner'), ('teacher', 'teacher')], max_length=45, verbose_name='role')),
                ('phones', django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message='Phone number must be in the format: 996XXX123456.', regex='^996\\d{9}$')]), blank=True, null=True, size=None, verbose_name='phones')),
                ('inn', models.PositiveIntegerField(default=1, unique=True, verbose_name='inn')),
                ('address', models.CharField(max_length=500, verbose_name='address')),
                ('is_staff', models.BooleanField(default=False, verbose_name='is staff')),
                ('joined', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='AbsenceReason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('is_deletable', models.BooleanField(default=True, verbose_name='is deletable')),
            ],
            options={
                'verbose_name': 'absence reason',
                'verbose_name_plural': 'absence reasons',
            },
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('address', models.CharField(max_length=500, verbose_name='address')),
            ],
            options={
                'verbose_name': 'branch',
                'verbose_name_plural': 'branches',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days_type', models.PositiveSmallIntegerField(choices=[(0, 'Odd'), (1, 'Even')], verbose_name='days type')),
                ('start_time', models.PositiveSmallIntegerField(choices=[(8, '8:00 - 9:00'), (9, '9:00 - 10:00'), (10, '10:00 - 11:00'), (11, '11:00 - 12:00'), (12, '12:00 - 13:00'), (13, '13:00 - 14:00'), (14, '14:00 - 15:00'), (15, '15:00 - 16:00'), (16, '16:00 - 17:00'), (17, '17:00 - 18:00'), (18, '18:00 - 19:00'), (19, '19:00 - 20:00'), (20, '20:00 - 21:00'), (21, '21:00 - 22:00')], verbose_name='start time')),
                ('started_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='started at')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.branch', verbose_name='branch')),
                ('current_teacher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='current teacher')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completion_timestamp', models.DateTimeField()),
                ('took_place', models.BooleanField(default=False)),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.group')),
            ],
            options={
                'verbose_name': 'lesson',
                'verbose_name_plural': 'lessons',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('batch_price', main.models.fields.MoneyField(decimal_places=2, max_digits=22, verbose_name='batch price')),
                ('single_price', main.models.fields.MoneyField(decimal_places=2, max_digits=22, verbose_name='single price')),
                ('max_student_count', models.PositiveSmallIntegerField(verbose_name='maximum number of students')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
            ],
            options={
                'verbose_name': 'plan',
                'verbose_name_plural': 'plans',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator(message='Phone number must be in the format: 996XXX123456.', regex='^996\\d{9}$')], verbose_name='phone')),
                ('fullname', models.CharField(max_length=255, verbose_name='full name')),
                ('birth_day', models.DateField(verbose_name='birth day')),
                ('balance', main.models.fields.MoneyField(decimal_places=2, default=0, max_digits=22, verbose_name='balance')),
                ('promoter', models.CharField(choices=[('instagram', 'instagram'), ('friend', 'friend'), ('banners', 'banners'), ('partners', 'partners'), ('used_to_go', 'used to go'), ('internet', 'internet')], max_length=255, verbose_name='promoter')),
                ('allow_loan', models.BooleanField(default=False, verbose_name='allow loan')),
                ('paused', models.BooleanField(default=False, verbose_name='paused')),
                ('phones', django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=12, validators=[django.core.validators.RegexValidator(message='Phone number must be in the format: 996XXX123456.', regex='^996\\d{9}$')]), blank=True, null=True, size=None, verbose_name='phones')),
                ('branch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.branch', verbose_name='branch')),
                ('curator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='curator')),
            ],
            options={
                'verbose_name': 'student',
                'verbose_name_plural': 'students',
                'permissions': (('manage_students_in_same_branch', 'Manage students in the same branch'),),
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='title')),
            ],
            options={
                'verbose_name': 'subject',
                'verbose_name_plural': 'subjects',
            },
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('address', models.CharField(max_length=255, verbose_name='address')),
                ('access_token', models.PositiveIntegerField(verbose_name='access token')),
            ],
            options={
                'verbose_name': 'terminal',
                'verbose_name_plural': 'terminals',
            },
        ),
        migrations.CreateModel(
            name='TeacherLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.lesson', verbose_name='lesson')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='teacher')),
            ],
            options={
                'verbose_name': 'teacher lesson',
                'verbose_name_plural': 'teacher lessons',
            },
        ),
        migrations.CreateModel(
            name='StudentLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson_price', main.models.fields.MoneyField(decimal_places=2, max_digits=22, verbose_name='lesson price')),
                ('absence_reason', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.absencereason', verbose_name='absence reason')),
                ('lesson', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.lesson', verbose_name='lesson')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.student', verbose_name='student')),
            ],
            options={
                'verbose_name': 'student lesson',
                'verbose_name_plural': 'student lessons',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', main.models.fields.MoneyField(decimal_places=2, max_digits=22, verbose_name='amount')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.student')),
                ('terminal', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.terminal')),
            ],
            options={
                'verbose_name': 'payment',
                'verbose_name_plural': 'payments',
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500, verbose_name='name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('last_changed', models.DateTimeField(auto_now=True, verbose_name='last changed')),
                ('branch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.branch', verbose_name='branch')),
                ('responsible', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='responsible')),
            ],
            options={
                'verbose_name': 'inventory',
                'verbose_name_plural': 'inventories',
            },
        ),
        migrations.AddField(
            model_name='group',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='main.subject', verbose_name='subject'),
        ),
        migrations.CreateModel(
            name='EarningRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', main.models.fields.MoneyField(decimal_places=2, max_digits=4, verbose_name='rate')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.group', verbose_name='group')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='teacher')),
            ],
            options={
                'verbose_name': 'earning rate',
                'verbose_name_plural': 'earning rates',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main.branch', verbose_name='branch'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='main.group', verbose_name='group')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.plan', verbose_name='plan')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='student')),
            ],
            options={
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscription',
                'unique_together': {('student', 'group')},
            },
        ),
    ]
