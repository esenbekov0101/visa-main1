from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as srz

from ..models import Student
from ..models import StudentLesson

from .lesson import LessonSerializer


class StudentSerializerForMembership(srz.ModelSerializer):
    class Meta:
        model = Student
        fields = ('url', 'id', 'phone', 'fullname')


class StudentLessonListSrz(srz.ModelSerializer):
    student = StudentSerializerForMembership()
    lesson = LessonSerializer()
    absence_reason = srz.SlugRelatedField('name', read_only=True)

    class Meta:
        model = StudentLesson
        fields = 'id', 'student', 'lesson', 'has_participated', 'absence_reason'


class StudentLessonAttendanceSrz(srz.ModelSerializer):
    class Meta:
        model = StudentLesson
        fields = 'id', 'has_participated', 'absence_reason'

    def validate_has_participated(self, has_participated):
        if has_participated is None:
            raise srz.ValidationError(
                _('null value not allowed'),
            )
        return has_participated

    def validate(self, attrs):
        if 'has_participated' not in attrs:
            raise srz.ValidationError({
                'has_participated': [
                    _('This field is required'),
                ]
            }, 'invalid')
        has_participated = attrs['has_participated']
        absence_reason = attrs.get('absence_reason')
        if has_participated and absence_reason:
            raise srz.ValidationError(
                {'absence_reason': [_(
                    'absence reason must not be null when student did not participated',
                )]}
            )
        return attrs

    def save(self, **kwargs):
        try:
            return super(StudentLessonAttendanceSrz, self).save(**kwargs)
        except IntegrityError as e:
            if any(['absence_reason_null_when_participated' in arg for arg in e.args]):
                raise srz.ValidationError(
                    {'absence_reason': [_(
                        'absence reason must not be null '
                        'when student did not participated',
                    )]}
                )

    def update(self, instance: StudentLesson, validated_data):
        if instance.lesson.took_place is None:
            raise srz.ValidationError(
                _('Could not process. Try again after marking the lesson as taken place')
            )
        if instance.lesson.took_place is False:
            raise srz.ValidationError(
                _('Could not process. Student can not participate to a cancelled lesson')
            )
        if instance.has_participated:
            raise srz.ValidationError(
                _('This student already marked as participated')
            )

        return super().update(instance, validated_data)
