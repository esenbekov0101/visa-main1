from rest_framework import serializers as srz

from .. import models


class SubjectSerializer(srz.ModelSerializer):
    class Meta:
        model = models.Subject
        fields = 'id', 'title',
