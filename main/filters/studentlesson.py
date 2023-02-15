from django_filters.rest_framework import FilterSet

from .. import models


class StudentLessonFilter(FilterSet):
    class Meta:
        model = models.StudentLesson
        fields = {
            'student': ['exact'],
            'lesson__group': ['exact'],
            'lesson__completion_timestamp': ['range', 'year', 'month'],
        }
