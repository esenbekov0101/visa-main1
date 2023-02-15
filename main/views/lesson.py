from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSetMixin

from main.models import Lesson
from main.permissions import HasBranch


class LessonViewSet(
    ViewSetMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView,
):
    authentication_classes = (IsAuthenticated, HasBranch)
    pagination_class = None

    def get_queryset(self):
        qs = Lesson.objects.filter(group__branch_id=self.request.user.branch_id)
        return qs
