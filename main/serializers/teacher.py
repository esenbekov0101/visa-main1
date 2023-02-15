from django.utils.timezone import now
from rest_framework import serializers as srz

from .fields import ChoiceField
from ..choices import Time, Day
from ..models import Group
from ..models import Teacher


class GroupsSrz(srz.HyperlinkedModelSerializer):
    subject = srz.SlugRelatedField('title', read_only=True)
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    student_count = srz.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ('url', 'name', 'subject', 'days_type', 'start_time',
                  'student_count', 'max_student_count')


class TeacherDetailSrz(srz.ModelSerializer):
    age = srz.SerializerMethodField('get_age')
    group_set = GroupsSrz(many=True)

    class Meta:
        model = Teacher
        fields = (
            'phone', 'fullname', 'phones', 'subjects', 'inn', 'address',
            'birth_day', 'group_set', 'age', 'comment',
        )

    def get_age(self, instance) -> int:
        today = now().today()
        born = instance.birth_day
        return today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )


class TeacherSerializer(srz.HyperlinkedModelSerializer):
    age = srz.SerializerMethodField('get_age')

    class Meta:
        model = Teacher
        fields = (
            'url', 'id', 'phone', 'fullname', 'phones', 'inn', 'address',
            'comment', 'birth_day', 'subjects', 'age',
        )
        extra_kwargs = {
            'url': {'view_name': 'teacher-detail'},
        }

    def get_age(self, instance) -> int:
        today = now().today()
        born = instance.birth_day
        return today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )


class TeacherFireSrz(srz.Serializer):
    comment = srz.CharField()
