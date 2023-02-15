from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from .. import filters
from .. import models
from .. import permissions as perm
from .. import serializers as srz


class PendingViewSet(
    ViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView,
):
    filter_backends = filters.FilterBackend, filters.SearchFilter
    filterset_class = filters.PendingFilter
    pagination_class = None
    search_fields = ('level',
                     'student__first_name', 'student__middle_name', 'student__last_name',
                     'student__phone',
                     'subject__title',
                     'teacher__fullname', 'teacher_phone', 'teacher_subjects',
                     )
    permission_classes = IsAuthenticated, perm.HasBranch,

    srz_map = {
        'create': srz.PendingCreateSrz,
        'list': srz.PendingListSrz,
    }

    def get_serializer_class(self):
        return self.srz_map.get(self.action) or srz.PendingListSrz

    def get_queryset(self):
        return models.Pending.objects

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: srz.PendingListSrz})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = srz.PendingListSrz(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
