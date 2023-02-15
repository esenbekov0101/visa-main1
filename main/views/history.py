from django.db.models import Q
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSetMixin

from main.filters import FilterBackend
from main.filters import HistoryFilter
from main.filters import TeacherHistoryFilter
from main.filters import SearchFilter
from main.models import History, Group
from main.models import TeacherHistory
from main.permissions import HasBranch


from main import serializers as srz


class HistoryViewSet(
    ViewSetMixin,
    mixins.ListModelMixin,
    GenericAPIView
):
    pagination_class = None
    permission_classes = IsAuthenticated, HasBranch
    filter_backends = FilterBackend, SearchFilter
    filterset_class = HistoryFilter
    search_fields = ('student__first_name', 'student__middle_name', 'student__last_name',
                     'student__phone', 'group__name', 'group__subject__title')
    serializer_class = srz.HistoryListSrz

    def get_queryset(self):
        qs = History.objects.filter(
            Q(group__branch=self.request.user.branch) |
            Q(student__branch=self.request.user.branch)
        )
        return qs


class TeacherHistoryViewSet(
    ViewSetMixin,
    mixins.ListModelMixin,
    GenericAPIView
):
    permission_classes = IsAuthenticated, HasBranch
    filter_backends = FilterBackend, SearchFilter
    filterset_class = TeacherHistoryFilter
    search_fields = ('teacher__fullname', 'teacher__phone',
                     'group__name', 'group__subject__title')
    serializer_class = srz.TeacherHistoryListSrz

    def get_queryset(self):
        qs = TeacherHistory.objects.filter(
            Q(group__branch=self.request.user.branch) |
            Q(teacher__branch=self.request.user.branch)
        )
        return qs
