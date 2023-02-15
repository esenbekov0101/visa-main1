from django.db.models import Case
from django.db.models import CharField
from django.db.models import OuterRef
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import Value
from django.db.models import When
from django.db.transaction import atomic
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from .. import filters
from .. import models
from .. import permissions as perm
from .. import serializers as srz


class AttendanceViewSet(ViewSetMixin,
                        mixins.ListModelMixin,
                        GenericAPIView):
    pagination_class = None
    permission_classes = IsAuthenticated, perm.HasBranch
    filter_backends = DjangoFilterBackend,
    filterset_class = filters.AttendanceFilter

    srz_map = {
        'took_place': srz.TookPlaceSrz,
    }

    def get_serializer_class(self):
        return self.srz_map.get(self.action) or srz.AttendanceSerializer

    def get_queryset(self):
        if self.action == 'took_place':
            return models.Lesson.objects
        qs = models.Lesson.objects.filter(
            group__started_at__isnull=False,
            group__branch=self.request.user.branch,
        ).order_by(
            'id',
            'studentlesson__id',
        ).prefetch_related(
            Prefetch('studentlesson_set',
                     models.StudentLesson.objects.annotate(
                         badge=Case(
                             When(Q(plan=1), Value('проб')),
                             When(Q(plan=2), Value('доп')),
                             default=Value(''),
                             output_field=CharField(max_length=10),
                         ),
                         status=Subquery(
                             models.History.objects.filter(
                                 group_id=OuterRef('lesson__group_id'),
                                 student_id=OuterRef('student_id'),
                             ).values('description')[:1],
                             default=Value(''),
                             output_field=CharField(max_length=500),
                         )
                     )
                     ),
            'group__current_teacher',
        )

        #  set reason=paused to student's lessons.
        # try:
        #     paused_reason = models.AbsenceReason.objects.get(id=1)
        #     for lesson in qs:
        #         student_lessons = lesson.studentlesson_set.filter(student__paused=True)
        #         student_lessons.update(absence_reason_id=paused_reason.id)
        # except models.AbsenceReason.DoesNotExist:
        #     pass
        return qs.distinct('id')

    @action(['put'], True, 'took-place')
    @atomic
    def took_place(self, *args, **kwargs):
        lesson = self.get_object()

        serializer = self.get_serializer(lesson, self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(took_place=True)
        if teacher := serializer.validated_data.get('teacher'):
            models.TeacherHistory.objects.create(
                group=lesson.group,
                manager=self.request.user.fullname,
                teacher=teacher,
                description=f'Подмена учителя со стороны: {teacher.fullname}'
            )
        took_place = serializer.validated_data['took_place']
        if took_place is False:
            comment = f'Отмена урока'
            if cm := serializer.validated_data.get('comment'):
                models.TeacherHistory.objects.create(
                    group=lesson.group,
                    manager=self.request.user.fullname,
                    teacher_id=instance.teacher_id,
                    description=comment + f', комментарий: {cm}'
                )
        return Response(status=status.HTTP_200_OK)
