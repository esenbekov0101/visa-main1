from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ViewSetMixin

from .. import models
from .. import serializers as srz


class SubjectViewSet(ViewSetMixin,
                     mixins.ListModelMixin,
                     GenericAPIView):
    pagination_class = None
    queryset = models.Subject.objects.all()
    serializer_class = srz.SubjectSerializer
