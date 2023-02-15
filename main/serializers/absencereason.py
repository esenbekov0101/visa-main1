from rest_framework import serializers as srz

from .. import models


class AbsenceReasonSerializer(srz.ModelSerializer):
    class Meta:
        model = models.AbsenceReason
        fields = 'id', 'name'
