from django.db.models import Sum, Exists, OuterRef, Q
from django.db.models.functions import Coalesce
from django.db.transaction import atomic
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as srz


from main import models
from .fields import ChoiceField
from ..choices import Day
from ..choices import Role
from ..choices import Time
from ..models.fields import MoneyField


class BookSrz(srz.ModelSerializer):
    class Meta:
        model = models.Book
        fields = ('name', 'price')


class StudentPKSrz(srz.PrimaryKeyRelatedField):
    def get_queryset(self):
        return models.Student.objects.filter(
            branch_id=self.context['request'].user.branch_id,
        )


class TeacherPKSrz(srz.PrimaryKeyRelatedField):
    def get_queryset(self):
        return models.User.objects.filter(
            branch_id=self.context['request'].user.branch_id,
            role=Role.TEACHER,
        )


class StudentSerializer(srz.HyperlinkedModelSerializer):
    status = srz.SerializerMethodField('get_status')
    age = srz.SerializerMethodField('get_age')

    class Meta:
        model = models.Student
        fields = 'url', 'id', 'status', 'phone', 'fullname', 'birth_day', 'age'

    def get_age(self, instance) -> int:
        today = now().today()
        born = instance.birth_day
        return today.year - born.year - (
            (today.month, today.day) < (born.month, born.day)
        )

    def get_status(self, instance: models.Student) -> str:
        if hasattr(instance, 'status') and instance.status:
            return f'{instance.status.description} ' \
                   f'{instance.status.comment or ""}'.strip()
        if group := self.context.get('group'):
            if history := models.History.objects.filter(
                student=instance,
                group=group,
            ).first():
                return f'{history.description} {history.comment or ""}'.strip()


class TeacherSrz(srz.HyperlinkedModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ('url', 'id', 'fullname')


class GroupCreateSrz(srz.ModelSerializer):
    current_teacher = TeacherPKSrz()

    class Meta:
        model = models.Group
        fields = ('id', 'name', 'level', 'subject', 'days_type', 'start_time', 'comment',
                  'current_teacher', 'started_at', 'max_student_count', 'book')
        extra_kwargs = {
            'started_at': {'read_only': True},
        }


class GroupChangeLevelSrz(srz.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ('level',)


class GroupChangeTeacherSrz(srz.ModelSerializer):
    current_teacher = TeacherPKSrz()

    class Meta:
        model = models.Group
        fields = ('current_teacher',)


class GroupUpdateSrz(srz.ModelSerializer):

    class Meta:
        model = models.Group
        fields = ('level', 'comment',)


class GroupListSrz(srz.HyperlinkedModelSerializer):
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    student_count = srz.SerializerMethodField(method_name='get_student_count')
    current_teacher = TeacherSrz(read_only=True)
    subject = srz.SlugRelatedField('title', read_only=True)

    class Meta:
        model = models.Group
        fields = (
            'url', 'id', 'name', 'level', 'subject', 'days_type', 'start_time',
            'comment', 'current_teacher', 'started_at', 'max_student_count',
            'student_count',
        )

    def get_student_count(self, instance=None) -> int:
        if instance:
            return instance.students.count()


class GroupTrialsSrz(srz.HyperlinkedModelSerializer):
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    subject = srz.SlugRelatedField('title', read_only=True)
    students = StudentSerializer(source='student_set', many=True)

    class Meta:
        model = models.Group
        fields = ('url', 'id', 'name', 'days_type', 'start_time', 'subject',
                  'students')

    def to_representation(self, instance):
        lessons = instance.lesson_set.filter(
            studentlesson__plan_id=1,
            took_place=False,
        ).distinct()
        students = []
        for lesson in lessons:
            student_lessons = lesson.studentlesson_set.filter(
                plan_id=1,
            ).select_related('student')
            for student_lesson in student_lessons:
                student_lesson.student.status = models.History.objects.filter(
                    student_id=student_lesson.student_id,
                    group=instance,
                ).first()
                students.append(student_lesson.student)
        instance.student_set = students
        representation = super().to_representation(instance)
        return representation


class GroupWithNoLessonSrz(srz.HyperlinkedModelSerializer):
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    subject = srz.SlugRelatedField('title', read_only=True)
    students = StudentSerializer(many=True)

    class Meta:
        model = models.Group
        fields = ('url', 'id', 'name', 'days_type', 'start_time', 'subject',
                  'students')

    def to_representation(self, instance):
        for student in instance.students.all():
            student.status = models.History.objects.filter(
                student_id=student.id,
                group=instance,
            ).first()
        representation = super().to_representation(instance)
        return representation


class GroupCompletedSrz(srz.HyperlinkedModelSerializer):
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    subject = srz.SlugRelatedField('title', read_only=True)
    students = StudentSerializer(source='student_set', many=True)

    class Meta:
        model = models.Group
        fields = ('url', 'id', 'name', 'days_type', 'start_time', 'subject',
                  'students')

    def to_representation(self, instance):
        students = models.Student.objects.filter(
            Exists(models.StudentLesson.objects.filter(
                student_id=OuterRef('pk'),
                lesson__group_id=instance.id,
                student__groups=instance,
            )),
            ~Exists(models.StudentLesson.objects.filter(
                Q(lesson__took_place=False) | Q(lesson__took_place__isnull=True),
                student_id=OuterRef('pk'),
                lesson__group_id=instance.id,
                student__groups=instance,
            ))
        )
        for student in students:
            student.status = models.History.objects.filter(
                    student_id=student.id,
                    group=instance,
                ).first()
        instance.student_set = students
        representation = super().to_representation(instance)
        return representation


class PendingSerializer(srz.ModelSerializer):
    student = StudentSerializer(srz.ModelSerializer, read_only=True)

    class Meta:
        model = models.Pending
        fields = ('id', 'student', 'created_at')


class GroupDetailSerializer(srz.ModelSerializer):
    days_type = ChoiceField(Day.choices)
    start_time = ChoiceField(Time.choices)
    students = StudentSerializer(many=True)
    unsubscribed = StudentSerializer(many=True)
    completed = StudentSerializer(many=True)
    trials = StudentSerializer(many=True)
    book = BookSrz(read_only=True)
    current_teacher = TeacherSrz(read_only=True)

    class Meta:
        model = models.Group
        fields = (
            'id', 'name', 'level', 'subject', 'days_type', 'start_time',
            'current_teacher', 'started_at', 'max_student_count', 'book', 'students',
            'unsubscribed', 'completed', 'trials', 'comment',
        )

    def to_representation(self, instance):
        lessons = instance.lesson_set.filter(
            studentlesson__plan_id=1,
            took_place=False,
        ).distinct()
        students = []
        for lesson in lessons:
            student_lessons = lesson.studentlesson_set.filter(
                plan_id=1,
            ).select_related('student')
            for student_lesson in student_lessons:
                student_lesson.student.status = models.History.objects.filter(
                    student_id=student_lesson.student_id,
                    group=instance,
                ).first()
                students.append(student_lesson.student)
        instance.trials = students

        students = models.Student.objects.filter(
            Exists(models.StudentLesson.objects.filter(
                student_id=OuterRef('pk'),
                lesson__group_id=instance.id,
                student__groups=instance,
            )),
            ~Exists(models.StudentLesson.objects.filter(
                Q(lesson__took_place=False) | Q(lesson__took_place__isnull=True),
                student_id=OuterRef('pk'),
                lesson__group_id=instance.id,
                student__groups=instance,
            ))
        )
        for student in students:
            student.status = models.History.objects.filter(
                    student_id=student.id,
                    group=instance,
                ).first()
        instance.completed = students

        representaion = super().to_representation(instance)

        return representaion


class StudentSubscribeSerializer(srz.Serializer):
    group = srz.PrimaryKeyRelatedField(queryset=models.Group.objects.all())
    comment = srz.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        group = attrs['group']
        student = self.context['student']
        if student.groups.filter(id=group.id).exists():
            raise srz.ValidationError(
                _('This student already subscribed to given group'),
            )

        return attrs


class StudentUnsubscribeSerializer(srz.Serializer):
    group = srz.PrimaryKeyRelatedField(queryset=models.Group.objects.all())
    comment = srz.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        group = attrs['group']
        student = self.context['student']
        if not student.groups.filter(id=group.id).exists():
            raise srz.ValidationError(
                _('This student is not subscribed to given group'),
            )

        return attrs

    def unsubscribe(self, validated_data):
        group = validated_data['group']
        student = self.context['student']
        studentlessons = models.StudentLesson.objects.exclude(
            Q(has_participated=True) | Q(lesson__took_place=True)
        ).filter(
            student=student,
            lesson__group=group,
        )
        left_balance = studentlessons.aggregate(
            total_price=Coalesce(Sum('lesson_price'), 0, output_field=MoneyField()),
        ).get('total_price', 0)
        student.balance += left_balance
        studentlessons.delete()
        student.groups.remove(group)
        student.past_groups.add(group)
        student.save()
        models.History.objects.create(
            student=student,
            group=group,
            manager=self.context['request'].user.fullname,
            description=f'Студент отписался(-ась) от курса {group.name}',
            comment=validated_data['comment'],
        )
        models.History.objects.create(
            student=student,
            group=group,
            description=f'{left_balance} сомов переведен на счет студента '
                        f'по остаткам уроков, количество уроков: {len(studentlessons)}',
        )


class GroupPendingCreateSerializer(srz.Serializer):
    student = StudentPKSrz()

    def validate(self, attrs):
        student = attrs['student']
        group = self.context['group']
        if group.students.filter(id=student.id).exists():
            raise srz.ValidationError(
                _('This student already subscribed to given group'),
            )
        if group.pendings.filter(student=student).exists():
            raise srz.ValidationError(
                _('This student already pending given group'),
            )

        return attrs

    def add_to_pending(self, validated_data):
        student = validated_data['student']
        group = self.context['group']
        return models.Pending.objects.create(student=student, group=group)


class GroupSellBook(srz.Serializer):
    student = StudentPKSrz(queryset=models.Student.objects)

    def validate(self, attrs):
        student = attrs['student']
        book = self.context['book']
        if student.balance < book.price:
            raise srz.ValidationError(
                _('Insufficient balance'),
            )
        if book.count < 1:
            raise srz.ValidationError(
                _('No book left to sell'),
            )

        return attrs

    @atomic
    def sell_book(self):
        student = self.validated_data['student']
        book = self.context['book']
        student.balance -= book.price
        book.count -= 1
        book.save()
        student.save()
        models.History.objects.create(
            student=student,
            group=self.context['group'],
            description=f'Cтудент совершил оплату {book.price} сомов '
                        f'на книгу {book.name}'
        )
