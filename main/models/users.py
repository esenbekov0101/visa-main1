from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.models.fields import ArrayField

from main.choices import Promoter
from main.choices import Role
from main.models.fields import MoneyField
from main.models.managers import UserManager
from main.models.managers import StudentManager
from main.validators import phone_regex_kg


class MyAnonymousUser(AnonymousUser):
    branch_id = -1

    def set_password(self, raw_password):
        return super().set_password(raw_password)

    def check_password(self, raw_password):
        return super(MyAnonymousUser, self).check_password(raw_password)

    def save(self):
        return super(MyAnonymousUser, self).save()

    def delete(self):
        return super().delete()


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(_('phone'), validators=[phone_regex_kg], max_length=255,
                             unique=True)
    fullname = models.CharField(_('full name'), max_length=255)
    birth_day = models.DateField(_('birth day'))
    subjects = models.CharField(_('subjects'), max_length=500, null=True, blank=True)
    role = models.CharField(_('role'), max_length=45, choices=Role.choices)
    branch = models.ForeignKey('Branch', models.DO_NOTHING,
                               verbose_name=_('branch'), null=True)
    phones = ArrayField(models.CharField(max_length=255),
                        verbose_name=_('phones'), null=True, blank=True)
    inn = models.CharField(_('inn'), max_length=14, unique=True)
    address = models.CharField(_('address'), max_length=500)
    comment = models.TextField(_('comment'), null=True, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    is_staff = models.BooleanField(_('is staff'), default=False)
    is_fired = models.BooleanField(_('is fired'), default=False)
    joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ('inn', 'birth_day')

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        try:
            group_model = ContentType.objects.get(
                app_label='auth', model='group').model_class()
            try:
                self.groups.clear()
                group, created = group_model.objects.get_or_create(name=self.role)
                self.groups.add(group)
                self.is_staff = True
            except group_model.DoesNotExist:
                pass
            except ValueError:
                pass
        except ContentType.DoesNotExist:
            pass

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.phone}-{self.fullname}'


class Teacher(User):
    objects = User.objects.filter(role=Role.TEACHER, is_fired=False)
    all_objects = User.objects.filter(role=Role.TEACHER)

    class Meta:
        proxy = True
        verbose_name = _('teacher')
        verbose_name_plural = _('teachers')


class Student(models.Model):
    # common fields
    phone = models.CharField(_('phone'), validators=[phone_regex_kg], max_length=255,
                             unique=True)
    first_name = models.CharField(_('first name'), max_length=45)
    middle_name = models.CharField(
        _('middle name'), max_length=45,
        null=True, blank=True,
    )
    last_name = models.CharField(_('last_name'), max_length=45)
    birth_day = models.DateField(_('birth day'))
    branch = models.ForeignKey('Branch', models.SET_NULL, null=True,
                               verbose_name=_('branch'))
    balance = MoneyField(_('balance'), max_digits=22, default=0)
    promoter = models.CharField(_('promoter'), max_length=255, choices=Promoter.choices)
    comment = models.TextField(_('comment'), null=True, blank=True)

    # administration fields
    paused = models.BooleanField(_('paused'), default=False)
    blacklist = models.BooleanField(_('blacklist'), default=False)
    phones = ArrayField(models.CharField(max_length=12, validators=[phone_regex_kg]),
                        verbose_name=_('phones'), null=True, blank=True)

    # management stuff
    curator = models.ForeignKey(User, models.SET_NULL, null=True,
                                verbose_name=_('curator'))

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    objects = StudentManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _('student')
        verbose_name_plural = _('students')
        permissions = (
            ('manage_students_in_same_branch', _('Manage students in the same branch')),
        )
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return f'{self.phone}-{self.fullname}'

    @property
    def fullname(self):
        return f'{self.last_name} {self.first_name} {self.middle_name or ""}'.strip()


class History(models.Model):
    student = models.ForeignKey(
        'Student', models.CASCADE,
        'histories', null=True, blank=True,
    )
    manager = models.CharField(_('actor'), max_length=255)
    description = models.TextField(_('description'))
    comment = models.TextField(_('comment'), null=True, blank=True)
    group = models.ForeignKey(
        'Group', models.SET_NULL,
        'student_histories', null=True, blank=True,
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('history')
        verbose_name_plural = _('histories')
        ordering = ('-created_at',)

    def __str__(self):
        return self.description


class TeacherHistory(models.Model):
    teacher = models.ForeignKey('Teacher', models.CASCADE, 'histories')
    manager = models.CharField(_('actor'), max_length=255)
    description = models.TextField(_('description'))
    comment = models.TextField(_('comment'), null=True, blank=True)
    group = models.ForeignKey(
        'Group', models.SET_NULL,
        'teacher_histories', null=True, blank=True,
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('teacher history')
        verbose_name_plural = _('teacher histories')
        ordering = ('-created_at',)

    def __str__(self):
        return self.description
