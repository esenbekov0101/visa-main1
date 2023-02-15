from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group as DjangoGroup
from django.utils.translation import gettext_lazy as _
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from rangefilter.filters import DateTimeRangeFilter

from main.admin import filters
from main.choices import Role
from main.forms import PaymentForm, BookChangeForm
from main.forms import TerminalForm
from main.models import AbsenceReason
from main.models import Book
from main.models import Branch
from main.models import CeleryTask
from main.models import EarningRate
from main.models import Group
from main.models import Inventory
from main.models import Lesson
from main.models import Payment
from main.models import Plan
from main.models import Student
from main.models import StudentLesson
from main.models import Subject
from main.models import Terminal
from main.models import User

admin.site.register(Subject)
admin.site.unregister(DjangoGroup)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    fields = ('name', 'batch_price', 'single_price', 'max_student_count', 'created_at')
    readonly_fields = ('created_at',)
    list_display = ('name', 'batch_price', 'single_price',
                    'max_student_count', 'created_at')

    def get_queryset(self, request):
        return super(PlanAdmin, self).get_queryset(request).exclude(id__in=(1, 2))


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_filter = ('branch',)
    search_fields = ('name',)
    readonly_fields = ('count',)

    form = BookChangeForm

    def render_change_form(
        self, request, cx, add=False, change=False, form_url="", obj=None
    ):
        cx['adminform'].form.fields['responsible'].queryset = User.objects.filter(
            role=Role.MANAGER,
        )
        return super(BookAdmin, self).render_change_form(
            request, cx, add, change, form_url, obj
        )


@admin.register(DjangoGroup)
class DjangoGroupAdmin(DjangoGroupAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    readonly_fields = ('started_at',)
    list_display = ('name', 'level', 'days_type', 'start_time', 'current_teacher',
                    'max_student_count',
                    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = 'id', 'group', 'completion_timestamp', 'took_place'
    readonly_fields = 'took_place',
    list_filter = 'took_place',


@admin.register(AbsenceReason)
class AbsenceReasonAdmin(admin.ModelAdmin):
    list_filter = 'is_deletable',


@admin.register(StudentLesson)
class StudentLesson(admin.ModelAdmin):
    list_display = 'id', 'lesson', 'student', 'absence_reason', 'lesson_price'
    list_editable = 'absence_reason',


admin.site.register(EarningRate)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = 'name', 'address'
    list_editable = 'address',


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = 'name', 'responsible', 'created', 'last_changed'
    search_fields = 'name', 'responsible__fullname', 'responsible__phone'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if not user.is_superuser:
            if user.groups.filter(name='кураторы').exists():
                return qs.filter(responsible=user)
        return qs

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not request.user.is_superuser:
            self.exclude = 'branch', 'responsible'
        return super().get_form(request, obj, change, **kwargs)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = 'created',
    list_display = '__str__', 'amount', 'student', 'terminal', 'created'
    search_fields = 'student__phone', 'student__fullname',
    list_filter = ('terminal',)
    raw_id_fields = ('student',)

    form = PaymentForm

    def render_change_form(
        self, request, cx, add=False, change=False, form_url="", obj=None
    ):
        if 'terminal' in cx['adminform'].form.fields:
            cx['adminform'].form.fields['terminal'].queryset = Terminal.objects.filter(
                id=1,
            )
        return super().render_change_form(request, cx, add, change, form_url, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if not user.is_superuser:
            if user.groups.filter(name='кураторы').exists():
                return qs.filter(student__branch=user.branch)
        return qs

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = 'phone', 'fullname', 'balance', 'paused'
    list_editable = 'paused',
    list_filter = filters.CuratorListFilter, 'paused'
    search_fields = ('first_name', 'last_name', 'phone')
    readonly_fields = 'balance',

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('manage_students_in_same_branch')

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('manage_students_in_same_branch')


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = 'name', 'address', 'access_token'
    list_editable = 'address', 'access_token'
    search_fields = 'name', 'address'

    form = TerminalForm


@admin.register(User)
class UserAdmin(UserAdmin, DynamicArrayMixin):
    fieldsets = (
        (None, {
            'fields': ('phone', 'fullname', 'role', 'branch', 'phones', 'password')
        }),
        (_('Regulate'),
         {'fields': ('is_active',)}
         )
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': ('inn', 'phone', 'birth_day', 'role', 'password1', 'password2')
        }),
    )
    ordering = 'phone',
    list_display = 'phone', 'fullname', 'role', 'joined',
    list_editable = 'role',
    list_filter = 'role', 'is_fired', 'is_superuser', 'is_staff',

    search_fields = 'phone', 'fullname'


@admin.register(CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_filter = ('status', ('date_done', DateTimeRangeFilter), 'name')
    fields = (
        'task_id', 'date_done', 'traceback', 'name', 'worker', 'retries', 'queue',
        'get_args', 'get_kwargs'
    )
    list_display = ('task_id', 'name', 'get_args', 'get_kwargs', 'date_done')
    readonly_fields = fields

    def get_args(self, obj):
        return obj.args.tobytes().decode()

    def get_kwargs(self, obj):
        return obj.kwargs.tobytes().decode()
