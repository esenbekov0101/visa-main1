from celery.schedules import crontab
from django.db.models import Exists, Q
from django.db.models import OuterRef
from django.utils.timezone import now

from main.models import Group
from main.models import History
from main.models import StudentLesson
from root.celery import app
from root.celery import atomic_celery_task


@atomic_celery_task(bind=True, name='unsubscribe students')
def unsubscribe_students(self):
    current_time = now()
    groups = Group.objects.all()
    for group in groups:
        students = group.students.filter(
            Exists(StudentLesson.objects.filter(
                student_id=OuterRef('pk'),
                lesson__group_id=group.id,
                student__groups=OuterRef('pk'),
            )),
            ~Exists(StudentLesson.objects.filter(
                Q(lesson__took_place=False) | Q(lesson__took_place__isnull=True),
                student_id=OuterRef('pk'),
                lesson__group_id=group.id,
                lesson__completion_timestamp__lte=current_time,
                student__groups=OuterRef('pk'),
            ))

        )
        histories = []
        description = 'Студент был отписан по причине не остатка уроков в группе'
        for student in students:
            histories.append(
                History(
                    group=group,
                    student=student,
                    description=description,
                    manager='Система'
                )
            )
        History.objects.bulk_create(histories, 100)
        group.students.remove(*students)
        group.unsubscribed.add(*students, through_defaults={'created_at': now()})


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **__):
    sender.add_periodic_task(
        crontab(hour=1, minute=0),
        unsubscribe_students.s(),
        name='unsubscribe students',
    )
