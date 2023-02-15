from django.utils.timezone import now
from rest_framework import serializers as srz

from main import models
from main.choices import Time, Day
from main.serializers.fields import ChoiceField


class StudentSrz(srz.ModelSerializer):
    age = srz.SerializerMethodField('get_age')

    class Meta:
        model = models.Student
        fields = ('id', 'phone', 'fullname', 'age')

    def get_age(self, instance) -> int:
        today = now().today()
        born = instance.birth_day
        return today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )


class PendingListSrz(srz.ModelSerializer):
    subject = srz.SlugRelatedField('title', read_only=True)
    student = StudentSrz(read_only=True)
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    teacher = srz.SlugRelatedField('fullname', read_only=True)

    class Meta:
        model = models.Pending
        fields = ('id', 'subject', 'level', 'teacher', 'days_type', 'start_time',
                  'student', 'created_at')


class PendingCreateSrz(srz.ModelSerializer):
    class Meta:
        model = models.Pending
        fields = ('id', 'subject', 'student', 'teacher', 'level', 'days_type',
                  'start_time', 'comment')
