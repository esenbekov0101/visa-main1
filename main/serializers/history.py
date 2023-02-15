from rest_framework import serializers as srz

from main.models import History
from main.models import Student
from main.models import Teacher


class StudentSrz(srz.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ('url', 'id', 'fullname', 'phone')


class TeacherSrz(srz.HyperlinkedModelSerializer):
    class Meta:
        model = Teacher
        fields = ('url', 'id', 'fullname', 'phone')


class HistoryListSrz(srz.ModelSerializer):
    student = StudentSrz(read_only=True)

    class Meta:
        model = History
        fields = ('id', 'manager', 'student', 'description', 'comment', 'created_at')


class TeacherHistoryListSrz(srz.ModelSerializer):
    teacher = TeacherSrz(read_only=True)

    class Meta:
        model = History
        fields = ('id', 'manager', 'teacher', 'description', 'comment', 'created_at')
