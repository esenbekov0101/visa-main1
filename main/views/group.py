from django.db.models import Count, Prefetch, Q, OuterRef, Exists
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from main import filters
from main import models
from main import permissions as perm
from main import serializers as srz


class GroupViewSet(ViewSetMixin,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericAPIView):
    permission_classes = IsAuthenticated, perm.HasBranch
    filter_backends = filters.FilterBackend,
    filterset_class = filters.GroupFilter

    srz_map = {
        'archived': srz.GroupListSrz,
        'create': srz.GroupCreateSrz,
        'list': srz.GroupListSrz,
        'with_no_lesson': srz.GroupWithNoLessonSrz,
        'completed': srz.GroupCompletedSrz,
        'retrieve': srz.GroupDetailSerializer,
        'trials': srz.GroupTrialsSrz,
        'change_teacher': srz.GroupChangeTeacherSrz,
        'change_level': srz.GroupChangeLevelSrz,
        'sell_book': srz.GroupSellBook,
        'update': srz.GroupUpdateSrz,
    }

    def get_serializer_class(self):
        serializer_class = self.srz_map.get(self.action)
        return serializer_class or srz.GroupCreateSrz

    def get_queryset(self):
        branch_id = self.request.user.branch_id
        qs = models.Group.objects.filter(
            branch_id=branch_id,
        ).annotate(
            student_count=Count('students'),
        )
        all_qs = models.Group.all_objects.filter(
            branch_id=branch_id,
        ).annotate(
            student_count=Count('students'),
        )

        if self.action == 'no_lesson':
            qs = qs.annotate(
                no_lesson=Count('students', Q(students__studentlesson__isnull=True)),
            ).prefetch_related('students')
            all_qs = all_qs.annotate(
                no_lesson=Count('students', Q(students__studentlesson__isnull=True)),
            ).prefetch_related('students')
        match self.action:
            case 'retrieve':
                qs = all_qs.prefetch_related(
                    Prefetch(
                        'students',
                        models.Student.objects.all(),
                    ),
                    Prefetch(
                        'students',
                        models.Student.objects.filter(
                            Exists(models.StudentLesson.objects.filter(
                                student_id=OuterRef('pk'),
                            )),
                            ~Exists(models.StudentLesson.objects.filter(
                                Q(
                                    lesson__took_place=False,
                                    lesson__took_place__isnull=True,
                                ),
                                student_id=OuterRef('pk'),
                            ))
                        ),
                        'completed',
                    ),
                    'unsubscribed',
                ).select_related('book')
            case 'trials':
                qs = qs.filter(
                    lesson__studentlesson__plan_id=1,
                    lesson__took_place=False,
                ).distinct()
            case 'with_no_lesson':
                qs = qs.distinct().filter(
                    ~Exists(models.StudentLesson.objects.filter(
                        lesson__group_id=OuterRef('pk'),
                    )),
                    Exists(models.Student.objects.filter(groups=OuterRef('pk')))
                ).prefetch_related(
                    Prefetch(
                        'students',
                        models.Student.objects.filter(
                            ~Exists(models.StudentLesson.objects.filter(
                                student_id=OuterRef('pk'),
                                lesson__group_id=OuterRef(OuterRef('pk'))
                            )
                            )
                        ),
                    ),
                )
            case 'completed':
                qs = qs.filter(
                    ~Exists(models.StudentLesson.objects.filter(
                        Q(lesson__took_place=False) | Q(lesson__took_place__isnull=True),
                        lesson__group_id=OuterRef('pk'),
                        lesson__took_place=False,
                    )),
                    Exists(models.StudentLesson.objects.filter(
                        lesson__group_id=OuterRef('pk'),
                        lesson__took_place=True,
                        student__groups=OuterRef('pk'),
                    )),
                )
            case 'archived':
                qs = models.Group.all_objects.filter(
                    branch_id=branch_id,
                    archived=True,
                ).annotate(
                    student_count=Count('students'),
                    no_lesson=Count('students', Q(students__studentlesson__isnull=True)),
                )

        return qs.order_by('start_time')

    def get_serializer_context(self):
        cx = super().get_serializer_context()
        if self.action == 'retrieve':
            group = self.get_object()
            cx['group'] = group
        return cx

    def perform_create(self, serializer):
        group = serializer.save(branch_id=self.request.user.branch_id)

        models.TeacherHistory.objects.create(
            teacher=serializer.validated_data['current_teacher'],
            manager=self.request.user.fullname,
            description=f'Преподватель назначен для группы {group.name}',
            group=group,
        )
        models.History.objects.create(
            group=group,
            manager=self.request.user.fullname,
            description=f'Создана группа {group.name}',
        )

    @atomic
    def perform_update(self, serializer):
        models.History.objects.create(
            manager=self.request.user.fullname,
            group=serializer.instance,
            description=serializer.validated_data.get('comment'),
        )
        serializer.save()

    @action(['put'], True, 'sell-book')
    def sell_book(self, *args, **__):
        group = self.get_object()
        book = group.book
        if not book:
            raise srz.ValidationError({
                'group': [_('This group has no book')]
            })
        serializer = self.get_serializer(
            data=self.request.data,
            context={
                'request': self.request,
                'book': book,
                'group': group,
            })
        serializer.is_valid(raise_exception=True)
        serializer.sell_book()
        student = serializer.validated_data['student']
        return Response(data={
            'book_price': book.price,
            'balance_left': student.balance,
        })

    @action(['put'], True, 'change-teacher')
    @atomic
    def change_teacher(self, *args, **__):
        group = self.get_object()
        serializer = self.get_serializer(
            instance=group,
            data=self.request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        teacher = serializer.validated_data['current_teacher']
        models.History.objects.create(
            group=group,
            manager=self.request.user.fullname,
            description=f'Преподаватель {teacher.fullname} назначен для этой группы'
        )
        models.TeacherHistory.objects.create(
            teacher=serializer.validated_data['current_teacher'],
            group=group,
            manager=self.request.user.fullname,
            description=f'Преподаватель назначен для группы {group.name}'
        )
        return Response()

    @action(['put'], True, 'change-level')
    @atomic
    def change_level(self, *args, **__):
        group = self.get_object()
        serializer = self.get_serializer(
            instance=group,
            data=self.request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        level = serializer.validated_data['level']
        models.History.objects.create(
            group=group,
            manager=self.request.user.fullname,
            description=f'Уровень группы изменен на: {level}'
        )
        return Response()

    @action(['get'], False, 'trials')
    def trials(self, *_, **__):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(instance=qs, many=True)
        flattened_result = []
        for group in serializer.data:
            for student in group.pop('students', []):
                flattened_result.append({**group, **student})
        return Response(data=flattened_result)

    @action(['get'], True, 'archive')
    @atomic
    def archive(self, *_r, **__):
        group = self.get_object()
        if models.Lesson.objects.filter(group=group, took_place=False).exists():
            return Response({
                'detail': _('Can not archive group which has active lessons'),
            }, status.HTTP_400_BAD_REQUEST)
        group.archived = True
        group.save()
        models.History.objects.create(
            group=group,
            manager=self.request.user.fullname,
            description='Группа архивировано',
        )
        return Response()

    @action(['get'], False, 'archived')
    def archived(self, *_, **__):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(instance=qs, many=True)
        return Response(data=serializer.data)

    @action(['get'], False, 'with-no-lesson')
    def with_no_lesson(self, *_, **__):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(instance=qs, many=True)
        flattened_result = []
        for group in serializer.data:
            for student in group.pop('students', []):
                flattened_result.append({**group, **student})
        return Response(data=flattened_result)

    @action(['get'], False, 'completed')
    def completed(self, *_, **__):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(instance=qs, many=True)
        flattened_result = []
        for group in serializer.data:
            for student in group.pop('students', []):
                flattened_result.append({**group, **student})
        return Response(data=flattened_result)
