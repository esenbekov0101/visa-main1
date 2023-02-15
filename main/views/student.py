from django.db.models import Count, Prefetch, Subquery, Q
from django.db.transaction import atomic
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from .. import permissions as perms
from .. import serializers as srz
from ..filters import FilterBackend
from ..filters import SearchFilter
from ..filters import StudentFilter
from ..models import Group
from ..models import History
from ..models import Pending
from ..models import Student
from ..models import StudentLesson


class StudentViewSet(ViewSetMixin,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     GenericAPIView):
    permission_classes = IsAuthenticated, perms.HasBranch
    filter_backends = FilterBackend, SearchFilter
    filterset_class = StudentFilter
    search_fields = ('first_name', 'middle_name', 'last_name', 'phone')

    srz_map = {
        'blacklist': srz.StudentBlackSrz,
        'calculate_fee': srz.CalculateFeeSrz,
        'create': srz.StudentCreateSerializer,
        'update': srz.StudentUpdateSrz,
        'partial_update': srz.StudentUpdateSrz,
        'subscribe': srz.StudentSubscribeSerializer,
        'unsubscribe': srz.StudentUnsubscribeSerializer,
        'add_to_pending': srz.StudentPendingSerializer,
        'pause': srz.StudentPauseSrz,
        'resume': srz.StudentPauseSrz,
        'add_lesson': srz.AddLessonSrz,
        'add_trial': srz.AddTrialLessonSrz,
        'add_additional': srz.AddAdditionalLessonSrz,
        'add_loan_lesson': srz.AddLoanLessonSrz,
        'retrieve': srz.StudentDetailSerializer,
        'transfer_balance': srz.TransferBalanceSrz,
        'whitelist': srz.StudentWhiteSrz,
        'options': srz.StudentOptionsSrz,
    }

    def get_serializer_class(self):
        serializer_class = self.srz_map.get(self.action)
        return serializer_class or srz.StudentListSerializer

    def get_queryset(self):
        branch_id = self.request.user.branch_id
        match self.action:
            case 'create':
                return Student.all_objects
            case 'options':
                return Student.all_objects
            case 'whitelist':
                return Student.all_objects.filter(blacklist=True)
            case 'blacklisted':
                return Student.all_objects.filter(blacklist=True)
            case 'retrieve':
                return Student.all_objects.prefetch_related(
                    Prefetch(
                        lookup='groups',
                        queryset=Group.objects.select_related(
                            'current_teacher',
                            'subject',
                            'book',
                        ).order_by('start_time'),
                    ),
                    'past_groups',
                    'pendings',
                )
            case 'list':
                return Student.objects.filter(branch_id=branch_id).annotate(
                    group_count=Count('groups'),
                    pending_count=Count('pendings'),
                )
        return Student.objects.filter(branch_id=branch_id)

    def get_serializer_context(self):
        cx = super(StudentViewSet, self).get_serializer_context()
        if self.action == 'retrieve':
            cx['student'] = self.get_object()
        return cx

    @atomic
    def create(self, request, *args, **kwargs):
        curator = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save(curator=curator, branch_id=curator.branch_id)
        History.objects.create(
            student=student,
            manager=curator.fullname,
            description='Добавлен студент'
        )
        success_headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status.HTTP_201_CREATED,
            headers=success_headers
        )

    @atomic
    def perform_update(self, serializer):
        description = srz.get_description(serializer)
        if not description:
            return
        History.objects.create(
            manager=self.request.user.fullname,
            student=serializer.instance,
            description=description,
            comment=serializer.validated_data.get('comment')
        )
        serializer.save()

    @action(['PUT'], detail=True)
    @atomic
    def subscribe(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(
            data=self.request.data,
            context={
                'request': self.request,
                'student': student,
            }
        )
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data['group']
        student.groups.add(group)
        Pending.objects.filter(
            student_id=student.id,
            subject_id=group.subject_id,
        ).delete()
        History.objects.create(
            student=student,
            manager=self.request.user.fullname,
            group=group,
            description=f'Подписался(-ась) на курс {group.name}',
            comment=serializer.validated_data['comment'],
        )
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(['PUT'], detail=True)
    @atomic
    def unsubscribe(self, *_, **__):
        serializer = self.get_serializer(
            data=self.request.data,
            context={
                'request': self.request,
                'student': self.get_object(),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.unsubscribe(serializer.validated_data)
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(['PUT'], detail=True, url_path='add-to-pending')
    def add_to_pending(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(
            data=self.request.data,
            context={
                'request': self.request,
                'student': self.get_object(),
            }
        )
        serializer.is_valid(raise_exception=True)

        pending = serializer.add_to_pending(serializer.validated_data)
        return Response(
            data={
                'id': pending.id,
                'student': pending.student_id,
                'created_at': pending.created_at,
                'teacher': pending.teacher.fullname,
                'start_time': pending.start_time,
                'subject': {
                    'id': pending.subject_id,
                    'title': pending.subject.title,
                }
            },
            status=status.HTTP_201_CREATED,
        )

    @action(['put'], True, url_path='add-lesson')
    def add_lesson(self, *_, **__):
        return self.add_lesson_base(*_, **__)

    @action(['put'], True, url_path='add-loan-lesson')
    def add_loan_lesson(self, *_, **__):
        return self.add_lesson_base(*_, **__)

    @action(['put'], True, url_path='add-trial')
    def add_trial(self, *_, **__):
        return self.add_lesson_base(*_, **__)

    @action(['put'], True, url_path='add-additional')
    def add_additional(self, *_, **__):
        return self.add_lesson_base(*_, **__)

    def add_lesson_base(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(
            data=self.request.data,
            context={
                'request': self.request,
                'student': student,
                'group_id': self.request.data.get('group'),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.add_lesson()
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(['post'], True, url_path='calculate-fee')
    def calculate_fee(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(
            data=self.request.data,
            context={
                'request': self.request,
                'student': student,
                'group_id': self.request.data.get('group'),
            }
        )
        serializer.is_valid(raise_exception=True)
        total_fee = serializer.calculate_total_fee(
            plan=serializer.validated_data['plan'],
            lesson_count=serializer.validated_data['lesson_count'],
        )
        return Response(
            data={'total_fee': total_fee},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(['put'], True, url_path='transfer-balance')
    @atomic
    def transfer_balance(self, *_, **__):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        branch_id = self.request.user.branch_id
        student = Student.objects.select_for_update().get(
            branch_id=branch_id, **filter_kwargs,
        )
        serializer = self.get_serializer(
            data=self.request.data,
            context={
                'request': self.request,
                'student': student,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.transfer(serializer.validated_data)
        return Response(
            data={
                'balance': student.balance,
            },
            status=status.HTTP_200_OK,
        )

    @action(['put'], True, url_path='blacklist')
    def blacklist(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        student.blacklist = True
        student.save()
        History.objects.create(
            student=student,
            manager=self.request.user.fullname,
            description=f'студент включен в черный список',
            comment=serializer.validated_data['comment'],
        )
        return Response()

    @action(['put'], True, url_path='whitelist')
    def whitelist(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        student.blacklist = False
        student.save()
        History.objects.create(
            student=student,
            manager=self.request.user.fullname,
            description=f'студент удален из черного списока',
            comment=serializer.validated_data['comment'],
        )
        return Response()

    @action(['get'], False, 'blacklisted')
    def blacklisted(self, *_, **__):
        qs = self.filter_queryset(self.get_queryset().filter(blacklist=True))
        serializer = self.get_serializer(instance=qs, many=True)
        return Response(data=serializer.data)

    @action(['put'], True, 'pause')
    @atomic
    def pause(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        student.paused = True
        student.save()
        History.objects.create(
            student=student,
            manager=self.request.user.fullname,
            description='Студент остановлен',
            comment=serializer.validated_data['comment'],
        )
        return Response(data=serializer.data)

    @action(['put'], True, 'resume')
    @atomic
    def resume(self, *_, **__):
        student = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        student.paused = False
        student.save()
        History.objects.create(
            student=student,
            manager=self.request.user.fullname,
            description='Студент возобновлен',
            comment=serializer.validated_data['comment'],
        )
        return Response(data=serializer.data)

    @action(['get'], True, 'options')
    def options(self, *_, **__):
        student = self.get_object()
        group_ids = Subquery(
            StudentLesson.objects.filter(
                student=student,
            ).values_list('lesson__group_id', flat=True))
        groups = Group.objects.filter(
            Q(id__in=group_ids) | Q(students=student),
        ).distinct()
        serializer = self.get_serializer(
            {
                'groups': groups,
            }
        )
        return Response(serializer.data)
