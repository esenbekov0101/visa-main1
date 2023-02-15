from datetime import timedelta

from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as srz

from ..choices import Day
from ..choices import Time
from ..models import Group
from ..models import Lesson
from ..models import Student
from ..models import StudentLesson
from ..models import Teacher

from .fields import ChoiceField
from .utils import verbose_timedelta


class TeacherPKSrz(srz.PrimaryKeyRelatedField):
    def get_queryset(self):
        qs = super(TeacherPKSrz, self).get_queryset()
        qs = qs.filter(branch_id=self.context['request'].user.branch_id)
        return qs


class TeacherSrz(srz.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'phone', 'fullname')


class StudentSrz(srz.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'fullname')


class StudentLessonSerializerForAttendance(srz.ModelSerializer):
    student = StudentSrz(read_only=True)
    absence_reason = srz.SlugRelatedField('name', read_only=True)
    badge = srz.CharField(read_only=True)
    status = srz.CharField(read_only=True)

    class Meta:
        model = StudentLesson
        fields = ('id', 'student', 'has_participated', 'absence_reason', 'badge',
                  'status')

    # def get_status(self, instance: StudentLesson) -> str:
    #     if history := History.objects.filter(
    #         student_id=instance.student_id,
    #         group_id=instance.lesson.group_id,
    #     ).first():
    #         return f'{history.description} {history.comment or ""}'.strip()
    #
    # def get_badge(self, instance: StudentLesson) -> str:
    #     if instance.plan_id == 1:
    #         return 'проб'
    #     elif instance.plan_id == 2:
    #         return 'доп'
    #     return ''


class GroupSerializerForAttendance(srz.ModelSerializer):
    current_teacher = TeacherSrz(read_only=True)
    subject_title = srz.SerializerMethodField()
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)

    class Meta:
        model = Group
        fields = ('id', 'name', 'current_teacher', 'subject_title', 'start_time',
                  'max_student_count', 'days_type', 'start_time')

    def get_subject_title(self, obj) -> str:
        return obj.subject.title


class AttendanceSerializer(srz.ModelSerializer):
    group = GroupSerializerForAttendance(read_only=True)
    students = StudentLessonSerializerForAttendance(
        source='studentlesson_set',
        many=True,
    )

    class Meta:
        model = Lesson
        fields = ('id', 'completion_timestamp', 'group', 'students', 'took_place')


class TookPlaceSrz(srz.ModelSerializer):
    took_place = srz.BooleanField()
    teacher = TeacherPKSrz(queryset=Teacher.objects, required=False)
    comment = srz.CharField(required=False)

    class Meta:
        model = Lesson
        fields = ('took_place', 'teacher', 'comment')

    def validate(self, attrs):
        if attrs['took_place'] is False and not attrs['comment']:
            raise srz.ValidationError(
                {'comment': _('required when canceling lesson')}
            )
        return attrs

    def update(self, instance: Lesson, validated_data):
        current_time = now()
        fifteen_minutes_early = timedelta(minutes=15)
        fifteen_minutes_later = timedelta(minutes=75)

        if instance.took_place is False:
            raise srz.ValidationError(
                _('Lesson already aborted')
            )
        if instance.took_place:
            raise srz.ValidationError(
                _('Lesson already taken place')
            )
        if instance.completion_timestamp - current_time > fifteen_minutes_early:
            delta = instance.completion_timestamp - fifteen_minutes_early - current_time
            verbose = verbose_timedelta(delta)
            raise srz.ValidationError(
                _('Can not process. Try it %(delta)s later') % {'delta': verbose}
             )
        if current_time - instance.completion_timestamp > fifteen_minutes_later:
            raise srz.ValidationError(
                _('Can not process. You had to marked this lesson earlier')
            )

        validated_data.pop('comment', None)

        return super().update(instance, validated_data)

