from rest_framework import serializers as srz

from ..models import Lesson


class LessonSerializer(srz.ModelSerializer):
    class Meta:
        model = Lesson
        fields = 'id', 'completion_timestamp', 'took_place'
