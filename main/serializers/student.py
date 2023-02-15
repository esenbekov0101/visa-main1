from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from django.db.models import F
from django.db.transaction import atomic
from django.utils.dateformat import format
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as srz

from .fields import ChoiceField
from .fields import MoneyField
from .utils import daterange
from ..choices import Day
from ..choices import Plan as PlanChoice
from ..choices import Time
from ..models import Book
from ..models import Group
from ..models import History
from ..models import Lesson
from ..models import Pending
from ..models import Plan
from ..models import Student
from ..models import StudentLesson
from ..models import Subject
from ..models import Teacher


class BookSrz(srz.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'name', 'price')


class GroupSrz(srz.HyperlinkedModelSerializer):
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    subject = srz.SlugRelatedField('title', read_only=True)
    current_teacher = srz.SlugRelatedField('fullname', read_only=True)
    student_count = srz.SerializerMethodField('get_student_count')
    status = srz.SerializerMethodField('get_status')
    book = BookSrz(read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'days_type', 'start_time', 'subject', 'current_teacher',
                  'student_count', 'max_student_count', 'status', 'book')

    def get_student_count(self, instance=None):
        if instance:
            return instance.students.count()

    def get_status(self, instance: Group) -> str:
        if student := self.context.get('student'):
            if history := History.objects.filter(
                student=student,
                group=instance,
            ).first():
                return f'{history.description} {history.comment or ""}'.strip()


class PendingSrz(srz.ModelSerializer):
    subject = srz.SlugRelatedField('title', read_only=True)
    start_time = ChoiceField(Time.choices)

    class Meta:
        model = Pending
        fields = ('id', 'subject', 'start_time', 'created_at')


class StudentCreateSerializer(srz.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ('url', 'id', 'phone', 'first_name', 'middle_name', 'last_name',
                  'phones', 'promoter', 'birth_day', 'comment')
        extra_kwargs = {
            'id': {'read_only': True}
        }


class StudentUpdateSrz(srz.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ('url', 'id', 'phone', 'first_name', 'middle_name', 'last_name',
                  'phones', 'promoter', 'birth_day', 'comment')


class StudentPauseSrz(srz.Serializer):
    comment = srz.CharField(required=True, allow_blank=False)


class StudentBlackSrz(srz.Serializer):
    comment = srz.CharField(required=True, allow_blank=False)


class StudentWhiteSrz(srz.Serializer):
    comment = srz.CharField(required=True, allow_blank=False)


class StudentListSerializer(srz.HyperlinkedModelSerializer):
    age = srz.SerializerMethodField('get_age')

    class Meta:
        model = Student
        fields = ('url', 'id', 'phone', 'first_name', 'middle_name', 'last_name',
                  'fullname', 'balance', 'birth_day', 'age', 'promoter',
                  'comment',
                  )

    def get_age(self, instance) -> int:
        today = now().today()
        born = instance.birth_day
        return today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )


class StudentDetailSerializer(srz.ModelSerializer):
    groups = GroupSrz(many=True)
    past_groups = GroupSrz(many=True)
    pendings = PendingSrz(many=True)
    age = srz.SerializerMethodField('get_age')

    class Meta:
        model = Student
        fields = (
            'id', 'phone', 'first_name', 'middle_name', 'last_name',
            'fullname', 'balance', 'promoter', 'phones',
            'birth_day', 'age', 'groups', 'past_groups', 'pendings', 'comment',
        )

    def get_age(self, instance) -> int:
        today = now().today()
        born = instance.birth_day
        return today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )


class FilteredPlanSrz(srz.PrimaryKeyRelatedField):
    def get_queryset(self):
        queryset = Plan.objects.all()
        student = self.context.get('student')
        if student:
            queryset = queryset.exclude(id__in=(1, 2)).filter(
                created_at__year__gte=student.created_at.year - 1,
            )
        group = Group.objects.filter(id=self.context.get('group_id')).first()

        if group:
            queryset = queryset.filter(max_student_count=group.max_student_count)

        return queryset


class CalculateFeeSrz(srz.Serializer):
    plan = FilteredPlanSrz(queryset=Plan.objects)
    group = srz.PrimaryKeyRelatedField(queryset=Group.objects)
    lesson_count = srz.IntegerField()

    @classmethod
    def calculate_total_fee(cls, plan: Plan, lesson_count: int) -> Decimal:
        return Decimal(Decimal(lesson_count / 12) * plan.batch_price if
                       lesson_count > 11 else lesson_count * plan.single_price)


class AddLessonBaseSrz(srz.Serializer):
    group = srz.PrimaryKeyRelatedField(queryset=Group.objects)
    start_from = srz.DateTimeField()
    comment = srz.CharField(required=False, allow_blank=True)

    def validate_start_from(self, start_from):
        current_time = now()
        if start_from.hour == 0 and start_from.minute == 0 and start_from.second == 0:
            start_from = start_from.replace(
                hour=current_time.hour,
                minute=current_time.minute,
                second=current_time.second,
                microsecond=current_time.microsecond,
                tzinfo=current_time.tzinfo
            )
        if start_from < current_time:
            raise srz.ValidationError(
                _('Should not be in past time'),
            )
        return start_from

    def add_lesson(self):
        student = self.context['student']
        group = self.validated_data['group']
        start_from = self.validated_data['start_from']
        plan = self.get_plan(self.validated_data)
        lesson_count = self.get_lesson_count(self.validated_data)
        total_fee = self.calculate_total_fee(plan, lesson_count)

        student.balance = F('balance') - total_fee
        student.save()

        last_lesson = Lesson.objects.filter(
            group=group,
            studentlesson__in=StudentLesson.objects.filter(student=student),
        ).order_by(
            '-completion_timestamp'
        ).first()
        if last_lesson is not None and last_lesson.completion_timestamp > start_from:
            last_time = last_lesson.completion_timestamp + timedelta(days=1)
            start_time = datetime(
                year=last_time.year,
                month=last_time.month,
                day=last_time.day,
                hour=group.start_time,
            )
        else:
            start_time = datetime(
                year=start_from.year,
                month=start_from.month,
                day=start_from.day,
                hour=group.start_time,
            )
        days = daterange(start_time, group.days, lesson_count)
        student_lessons = []
        lesson_price = Decimal(total_fee / lesson_count)
        for day in days:
            try:
                lesson = Lesson.objects.get(
                    group=group,
                    completion_timestamp=day,
                )
            except Lesson.DoesNotExist:
                lesson = Lesson.objects.create(
                    group=group,
                    teacher=group.current_teacher,
                    completion_timestamp=day,
                )
            student_lessons.append(StudentLesson(
                student=student,
                lesson=lesson,
                lesson_price=lesson_price,
                plan=plan,
            ))
        StudentLesson.objects.bulk_create(student_lessons)

        desc_text = f'Cтудент совершил оплату на курс {group.name}, с ' \
                    f'{format(days[0], "d-M Y")} до ' \
                    f'{format(days[-1], "d-M Y")}, количество уроков: ' \
                    f'{lesson_count}, за {total_fee} сом'
        if plan.id == 2:
            desc_text = f'Студенту дано доп. уроки в количестве: {lesson_count}, на ' \
                        f'курс {group.name}, с {format(days[0], "d-M Y")} до ' \
                        f'{format(days[-1], "d-M Y")}'
        History.objects.create(
            student=student,
            manager=self.context['request'].user.fullname,
            group=group,
            description=desc_text,
            comment=self.validated_data.get('comment'),
        )

    def get_plan(self, attrs) -> Plan:
        raise NotImplementedError()

    def get_lesson_count(self, attrs) -> int:
        raise NotImplementedError()

    @classmethod
    def calculate_total_fee(cls, plan: Plan, lesson_count: int) -> Decimal:
        return Decimal(Decimal(lesson_count / 12) * plan.batch_price if
                       lesson_count > 11 else lesson_count * plan.single_price)


class AddLessonSrz(AddLessonBaseSrz):
    plan = FilteredPlanSrz(queryset=Plan.objects)
    lesson_count = srz.IntegerField(min_value=1, max_value=12 * 12)

    def validate(self, attrs):
        student = self.context['student']
        group = attrs['group']
        plan = self.get_plan(attrs)
        lesson_count = self.get_lesson_count(attrs)
        if group not in student.groups.all():
            raise srz.ValidationError(
                {
                    'group': _('This student not subscribed to given group.')
                }
            )
        total_fee = self.calculate_total_fee(plan, lesson_count)
        if student.balance < total_fee:
            raise srz.ValidationError(
                {
                    'student': _('Insufficient balance to complete this payment')
                }
            )
        return attrs

    @atomic
    def add_lesson(self):
        return super(AddLessonSrz, self).add_lesson()

    def get_plan(self, attrs) -> Plan:
        return attrs['plan']

    def get_lesson_count(self, attrs) -> int:
        return attrs['lesson_count']


class AddTrialLessonSrz(AddLessonBaseSrz):
    comment = srz.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        group = attrs['group']
        student = self.context['student']
        if group in student.groups.all():
            raise srz.ValidationError(
                {
                    'group': [_('This student already subscribed to given group.')]
                },
                'not-available',
            )
        if student.studentlesson_set.filter(
            lesson__group=group,
        ).exists():
            raise srz.ValidationError(
                {
                    'group': [_('This student already had lesson from this group')]
                },
                'not-available',
            )

        return attrs

    @atomic
    def add_lesson(self):
        student = self.context['student']
        group = self.validated_data['group']
        start_from = self.validated_data['start_from']
        plan = self.get_plan(self.validated_data)
        lesson_count = self.get_lesson_count(self.validated_data)

        start_time = datetime(
            year=start_from.year,
            month=start_from.month,
            day=start_from.day,
            hour=group.start_time,
        )
        day = daterange(start_time, group.days, lesson_count)[0]
        lesson_price = 0
        try:
            lesson = Lesson.objects.get(
                group=group,
                completion_timestamp=day,
            )
        except Lesson.DoesNotExist:
            lesson = Lesson.objects.create(
                group=group,
                teacher=group.current_teacher,
                completion_timestamp=day,
            )
        student_lesson = StudentLesson.objects.create(
            student=student,
            lesson=lesson,
            lesson_price=lesson_price,
            plan=plan,
        )
        History.objects.create(
            student=student,
            manager=self.context['request'].user.fullname,
            group=group,
            description=f'Придет на проб. занятие в {format(day, "d-b")}',
            comment=self.validated_data['comment'],
        )
        return student_lesson

    def get_plan(self, attrs) -> Plan:
        return Plan.objects.get(id=PlanChoice.TRIAL)

    def get_lesson_count(self, attrs) -> int:
        return 1


class AddLoanLessonSrz(AddLessonBaseSrz):
    comment = srz.CharField(required=False, allow_blank=True)
    plan = FilteredPlanSrz(queryset=Plan.objects)

    def validate(self, attrs):
        group = attrs['group']
        student = self.context['student']
        if group not in student.groups.all():
            raise srz.ValidationError(
                {
                    'group': [_('This student not subscribed to given group.')]
                },
                'not-available',
            )
        if student.balance < 0:
            raise srz.ValidationError(
                {
                    'group': [_('This student already has unpaid loan')]
                },
                'not-available',
            )

        return attrs

    @atomic
    def add_lesson(self):
        student = self.context['student']
        group = self.validated_data['group']
        start_from = self.validated_data['start_from']
        plan = self.get_plan(self.validated_data)
        lesson_count = 1

        start_time = datetime(
            year=start_from.year,
            month=start_from.month,
            day=start_from.day,
            hour=group.start_time,
        )
        day = daterange(start_time, group.days, lesson_count)[0]
        lesson_price = plan.single_price

        try:
            lesson = Lesson.objects.get(
                group=group,
                completion_timestamp=day,
            )
        except Lesson.DoesNotExist:
            lesson = Lesson.objects.create(
                group=group,
                teacher=group.current_teacher,
                completion_timestamp=day,
            )

        student.balance = F('balance') - lesson_price
        student.save()

        student_lesson = StudentLesson.objects.create(
            student=student,
            lesson=lesson,
            lesson_price=lesson_price,
            plan=plan,
        )
        History.objects.create(
            student=student,
            manager=self.context['request'].user.fullname,
            group=group,
            description=f'Дано занятие в долг. {format(day, "d-b")}',
            comment=self.validated_data['comment'],
        )
        return student_lesson

    def get_plan(self, attrs) -> Plan:
        return attrs['plan']

    def get_lesson_count(self, attrs) -> int:
        return 1


class AddAdditionalLessonSrz(AddLessonBaseSrz):
    lesson_count = srz.IntegerField(min_value=1, max_value=12 * 12)
    comment = srz.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        group = attrs['group']
        student = self.context['student']
        if group not in student.groups.all():
            raise srz.ValidationError(
                {
                    'group': _('This student not subscribed to given group.')
                }
            )

        return attrs

    @atomic
    def add_lesson(self):
        super(AddAdditionalLessonSrz, self).add_lesson()

    def get_plan(self, attrs) -> Plan:
        return Plan.objects.get(id=PlanChoice.ADDITIONAL)

    def get_lesson_count(self, attrs) -> int:
        return self.validated_data['lesson_count']


class TransferBalanceSrz(srz.Serializer):
    amount = MoneyField()
    receiver = srz.SlugRelatedField('phone', queryset=Student.objects)
    comment = srz.CharField()

    def validate_amount(self, amount):
        sender = self.context['student']
        if sender.balance < amount:
            raise srz.ValidationError(
                _('Insufficient balance')
            )
        return amount

    def transfer(self, validated_data):
        sender = self.context['student']
        receiver = validated_data['receiver']
        amount = validated_data['amount']
        sender.balance -= amount
        receiver.balance += amount
        sender.save()
        receiver.save()
        History.objects.create(
            student=sender,
            manager=self.context['request'].user.fullname,
            description=f'перевод баланса к студенту {receiver.phone}, '
                        f'сумма: {amount}, остаток: {sender.balance}',
            comment=self.validated_data['comment'],
        )
        History.objects.create(
            student=receiver,
            manager=self.context['request'].user.fullname,
            description=f'перевод баланса от студента {sender.phone}, '
                        f'сумма: {amount}, остаток: {receiver.balance}',
            comment=self.validated_data['comment'],
        )


class StudentPendingSerializer(srz.Serializer):
    subject = srz.PrimaryKeyRelatedField(queryset=Subject.objects)
    teacher = srz.PrimaryKeyRelatedField(
        queryset=Teacher.objects,
        required=False,
        allow_empty=True,
    )
    level = srz.CharField()
    start_time = srz.ChoiceField(Time.choices)

    def validate(self, attrs):
        subject = attrs['subject']
        student = self.context['student']
        if student.pendings.filter(subject=subject).exists():
            raise srz.ValidationError(
                _('This student already pending given group'),
            )

        return attrs

    def add_to_pending(self, validated_data):
        student = self.context['student']
        return Pending.objects.create(student=student, **validated_data)


class StudentOptionsSrz(srz.Serializer):
    groups = GroupSrz(many=True)
