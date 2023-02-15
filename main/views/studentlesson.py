from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSetMixin

from .. import filters
from .. import models
from .. import permissions as perm
from .. import serializers as srz


class StudentLessonViewSet(ViewSetMixin,
                           mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           GenericAPIView):
    pagination_class = None
    permission_classes = IsAuthenticated, perm.HasBranch
    filter_backends = DjangoFilterBackend,
    filterset_class = filters.StudentLessonFilter

    srz_map = {
        'update': srz.StudentLessonAttendanceSrz,
        'partial_update': srz.StudentLessonAttendanceSrz,
        'list': srz.StudentLessonListSrz,
    }

    def get_serializer_class(self):
        return self.srz_map.get(self.action) or srz.StudentLessonListSrz

    def get_queryset(self):
        qs = models.StudentLesson.objects.filter(
            student__branch_id=self.request.user.branch_id,
        )

        # if self.action in ('update', 'partial_update'):
        #     return qs.filter(
        #         lesson__took_place=True,
        #     )

        return qs
