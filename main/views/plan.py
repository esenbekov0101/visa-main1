from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ViewSetMixin


from .. import filters
from .. import models
from .. import serializers as srz


class PlanViewSet(ViewSetMixin,
                  mixins.ListModelMixin,
                  GenericAPIView):
    pagination_class = None
    queryset = models.Plan.objects.exclude(id__in=(1, 2))
    serializer_class = srz.PlanListSerializer
    filter_backends = filters.FilterBackend,
    filterset_class = filters.PlanFilter
