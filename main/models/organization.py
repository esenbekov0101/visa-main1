from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from main.choices import Day
from main.choices import TaskStatus
from main.choices import Time
from main.models.fields import MoneyField
from main.models.managers import GroupManager


class Branch(models.Model):
    name = models.CharField(_('name'), max_length=255)
    address = models.CharField(_('address'), max_length=500)

    class Meta:
        verbose_name = _('branch')
        verbose_name_plural = _('branches')

    def __str__(self):
        return self.name


class Inventory(models.Model):
    name = models.CharField(_('name'), max_length=500)
    branch = models.ForeignKey(Branch, models.SET_NULL, null=True,
                               verbose_name=_('branch'))
    responsible = models.ForeignKey('User', models.SET_NULL, null=True,
                                    verbose_name=_('responsible'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    last_changed = models.DateTimeField(_('last changed'), auto_now=True)

    class Meta:
        verbose_name = _('inventory')
        verbose_name_plural = _('inventories')

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(_('name'), max_length=500)
    subject = models.ForeignKey('Subject', models.SET_NULL,
                                'book_set', null=True, verbose_name=_('subject'))
    branch = models.ForeignKey(Branch, models.SET_NULL, null=True,
                               verbose_name=_('branch'))
    count = models.PositiveSmallIntegerField(_('count'))
    price = MoneyField(_('price'), max_digits=22)
    responsible = models.ForeignKey('User', models.SET_NULL, null=True,
                                    verbose_name=_('responsible'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    last_changed = models.DateTimeField(_('last changed'), auto_now=True)

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __str__(self):
        return self.name


class Subject(models.Model):
    title = models.CharField(_('title'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')

    def __str__(self):
        return self.title


class Plan(models.Model):
    name = models.CharField(_('name'), max_length=255)
    batch_price = MoneyField(_('batch price'), max_digits=22)
    single_price = MoneyField(_('single price'), max_digits=22)
    max_student_count = models.PositiveSmallIntegerField(_('maximum number of students'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('plan')
        verbose_name_plural = _('plans')

    def __str__(self):
        return self.name


class Unsubscribed(models.Model):
    group = models.ForeignKey('Group', models.CASCADE, related_name='past_students')
    student = models.ForeignKey('Student', models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('group', 'student')


class Group(models.Model):
    name = models.CharField(_('name'), max_length=255, unique=True)
    level = models.CharField(_('level'), max_length=255, null=True, blank=True)
    branch = models.ForeignKey('Branch', models.CASCADE, verbose_name=_('branch'))
    subject = models.ForeignKey('Subject', models.CASCADE, 'groups',
                                verbose_name=_('subject'))
    students = models.ManyToManyField('Student', 'groups')
    unsubscribed = models.ManyToManyField('Student', 'past_groups', through=Unsubscribed)
    max_student_count = models.PositiveSmallIntegerField(_('maximum number of students'))
    days_type = models.PositiveSmallIntegerField(_('days type'), choices=Day.choices)
    start_time = models.PositiveSmallIntegerField(_('start time'), choices=Time.choices)
    current_teacher = models.ForeignKey('Teacher', models.SET_NULL, null=True,
                                        verbose_name=_('current teacher'))
    comment = models.TextField(_('comment'), null=True, blank=True)
    book = models.ForeignKey('Book', models.SET_NULL, null=True, blank=True)
    archived = models.BooleanField(_('is archived'), default=False)
    started_at = models.DateTimeField(_('started at'), null=True, auto_now_add=True)

    objects = GroupManager()
    all_objects = Manager()

    @property
    def end_time(self):
        return self.start_time + 1

    @property
    def get_days(self) -> str:
        return Day(self.days_type).label

    @property
    def get_time(self) -> str:
        return Time(self.start_time).label

    @property
    def days(self):
        return [1, 3, 5] if self.days_type else [0, 2, 4]

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')
        ordering = ('start_time', )
        unique_together = ('days_type', 'start_time', 'current_teacher', 'archived')

    def __str__(self):
        return f'{self.name} {Day(self.days_type).label} {Time(self.start_time).label}'


class Pending(models.Model):
    student = models.ForeignKey('Student', models.CASCADE,
                                'pendings', verbose_name=_('student'))
    subject = models.ForeignKey('Subject', models.CASCADE,
                                'pendings', verbose_name=_('group'))
    level = models.CharField(_('level'), max_length=255)
    teacher = models.ForeignKey('Teacher', models.SET_NULL, null=True, blank=True)
    days_type = models.PositiveSmallIntegerField(_('days type'), choices=Day.choices)
    start_time = models.PositiveSmallIntegerField(
        _('start time'), choices=Time.choices, null=True, blank=True,
    )
    comment = models.CharField(_('comment'), max_length=500)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        unique_together = ('subject', 'student')


class Lesson(models.Model):
    group = models.ForeignKey(Group, models.SET_NULL, null=True)
    teacher = models.ForeignKey('Teacher', models.RESTRICT)
    completion_timestamp = models.DateTimeField()
    took_place = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        unique_together = (
            ('group', 'completion_timestamp'),
            ('teacher', 'completion_timestamp'),
        )

    def __str__(self):
        return f'{self.group.subject.title} {self.completion_timestamp}'


class AbsenceReason(models.Model):
    name = models.CharField(_('name'), max_length=255, unique=True)
    is_deletable = models.BooleanField(_('is deletable'), default=True)

    class Meta:
        verbose_name = _('absence reason')
        verbose_name_plural = _('absence reasons')

    def __str__(self):
        return self.name


class StudentLesson(models.Model):
    student = models.ForeignKey('Student', models.SET_NULL, null=True,
                                verbose_name=_('student'))
    lesson = models.ForeignKey(Lesson, models.SET_NULL, null=True,
                               verbose_name=_('lesson'))
    plan = models.ForeignKey(Plan, models.RESTRICT)
    has_participated = models.BooleanField(_('has participated'), default=False)
    absence_reason = models.ForeignKey('AbsenceReason', models.SET_NULL, null=True,
                                       blank=True, verbose_name=_('absence reason'))
    lesson_price = MoneyField(_('lesson price'), max_digits=22)

    class Meta:
        verbose_name = _('student lesson')
        verbose_name_plural = _('student lessons')
        # TODO: add constraint to db.
        # constraints = (
        #     models.CheckConstraint(
        #         check=Q(
        #             Q(has_participated=False),
        #             Q(absence_reason__isnull=False),
        #             _connector=Q.OR),
        #         name='absence_reason_null_when_participated',
        #     ),
        # )


class CeleryTask(models.Model):
    id = models.IntegerField(primary_key=True)
    task_id = models.CharField(_('task id'), unique=True, max_length=155,
                               blank=True, null=True)
    status = models.CharField(_('status'), max_length=45, choices=TaskStatus.choices)
    result = models.BinaryField(_('result'), blank=True, null=True)
    date_done = models.DateTimeField(_('date done'), blank=True, null=True)
    traceback = models.TextField(_('traceback'), blank=True, null=True)
    name = models.CharField(_('name'), max_length=155, blank=True, null=True)
    args = models.BinaryField(_('args'), blank=True, null=True)
    kwargs = models.BinaryField(_('kwargs'), blank=True, null=True)
    worker = models.CharField(_('worker'), max_length=155, blank=True, null=True)
    retries = models.IntegerField(_('retries'), blank=True, null=True)
    queue = models.CharField(_('queue'), max_length=155, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'celery_taskmeta'
        verbose_name = _('celery task')
        verbose_name_plural = _('celery tasks')

    def __str__(self):
        return self.task_id or self.id


class CeleryTaskset(models.Model):
    id = models.IntegerField(primary_key=True)
    taskset_id = models.CharField(unique=True, max_length=155, blank=True, null=True)
    result = models.BinaryField(blank=True, null=True)
    date_done = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'celery_tasksetmeta'
