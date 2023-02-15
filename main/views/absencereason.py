from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ViewSetMixin

from .. import models
from .. import serializers as srz


class AbsenceReasonViewSet(ViewSetMixin,
                           mixins.ListModelMixin,
                           GenericAPIView):
    pagination_class = None
    serializer_class = srz.AbsenceReasonSerializer
    queryset = models.AbsenceReason.objects.all()
