from django.db.models import Prefetch, Count
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from .. import filters
from .. import models
from .. import permissions as perm
from .. import serializers as srz
from ..choices import Role


class TeacherViewSet(ViewSetMixin,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     GenericAPIView):
    pagination_class = None
    permission_classes = IsAuthenticated, perm.HasBranch
    serializer_class = srz.TeacherSerializer
    filter_backends = filters.SearchFilter,
    search_fields = ('fullname', 'inn', 'phone')

    srz_map = {
        'retrieve': srz.TeacherDetailSrz,
        'fire': srz.TeacherFireSrz,
    }

    def get_serializer_class(self):
        return self.srz_map.get(self.action, srz.TeacherSerializer)

    def get_permissions(self):
        perms = super(TeacherViewSet, self).get_permissions()
        if self.action in ('hire', 'fire', 'fired'):
            perms.append(perm.IsManager())

        return perms

    def get_queryset(self):
        branch_id = self.request.user.branch_id
        qs = models.Teacher.objects.filter(branch_id=branch_id)
        if self.action in ('hire', 'fire', 'fired'):
            return models.Teacher.all_objects.filter(branch_id=branch_id)
        if self.action == 'retrieve':
            return qs.prefetch_related(
                Prefetch(
                    'group_set',
                    models.Group.objects.annotate(
                        student_count=Count('students'),
                    ).order_by('start_time'),
                )
            )
        return qs

    @atomic
    def perform_create(self, serializer):
        teacher = serializer.save(
            branch_id=self.request.user.branch_id,
            role=Role.TEACHER,
        )
        models.TeacherHistory.objects.create(
            teacher=teacher,
            manager=self.request.user.fullname,
            description='Преподаватель принят на работу',
        )

    @atomic
    def perform_update(self, serializer):
        description = srz.get_description(serializer)
        if not description:
            return
        models.TeacherHistory.objects.create(
            manager=self.request.user.fullname,
            teacher=serializer.instance,
            description=description,
            comment=serializer.validated_data.get('comment')
        )
        serializer.save()

    @action(['get'], True, 'hire')
    @atomic
    def hire(self, *_, **__):
        teacher = self.get_object()
        teacher.is_fired = False
        teacher.save()
        models.TeacherHistory.objects.create(
            teacher=teacher,
            manager=self.request.user.fullname,
            description='Преподаватель заново принят на работу'
        )
        return Response(status=status.HTTP_200_OK)

    @action(['put'], True, 'fire')
    @atomic
    def fire(self, *_a, **__):
        teacher = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        groups = models.Group.objects.filter(current_teacher=teacher).exists()
        lessons = models.Lesson.objects.filter(
            teacher=teacher,
            took_place=False,
        ).exists()
        if groups or lessons:
            return Response(
                {'detail': _('This teacher has active groups or lessons. '
                             'You should replace them with another teacher '
                             'before firing the teacher.'),
                 },
                status.HTTP_400_BAD_REQUEST,
            )
        teacher.is_fired = True
        teacher.save()
        models.TeacherHistory.objects.create(
            teacher=teacher,
            manager=self.request.user.fullname,
            description='Преподаватель уволен',
            comment=serializer.validated_data['comment']
        )
        return Response(status=status.HTTP_200_OK)

    @action(['get'], False, 'fired')
    def fired(self, *_a, **__):
        qs = self.filter_queryset(self.get_queryset()).filter(is_fired=True)
        serializer = self.get_serializer(instance=qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
