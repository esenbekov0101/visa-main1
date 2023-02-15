import django_filters as filters
from django_filters.rest_framework import FilterSet

from ..models import Group
from ..models import History
from ..models import Student
from ..models import Teacher
from ..models import TeacherHistory


class HistoryFilter(FilterSet):
    student = filters.ModelChoiceFilter(queryset=Student.all_objects)
    group = filters.ModelChoiceFilter(queryset=Group.all_objects)

    class Meta:
        model = History
        fields = {
            'student': ['exact'],
            'group': ['exact'],
            'group__subject': ['exact'],
        }


class TeacherHistoryFilter(FilterSet):
    teacher = filters.ModelChoiceFilter(queryset=Teacher.all_objects)
    group = filters.ModelChoiceFilter(queryset=Group.all_objects)

    class Meta:
        model = TeacherHistory
        fields = {
            'teacher': ['exact'],
            'group': ['exact'],
            'group__subject': ['exact'],
        }
