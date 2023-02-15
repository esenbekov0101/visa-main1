from rest_framework import serializers as srz

from .. import models


class PlanListSerializer(srz.ModelSerializer):
    subject = srz.SlugRelatedField('title', read_only=True)

    class Meta:
        model = models.Plan
        fields = 'id', 'subject', 'batch_price', 'single_price', 'max_student_count'
