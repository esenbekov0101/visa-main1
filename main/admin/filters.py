from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from main import choices
from main import models


class CuratorListFilter(admin.SimpleListFilter):
    title = _('By curator')

    def lookups(self, request, model_admin):
        tuple([obj.id, obj.phone] for obj in models.User.objects.filter(role=choices.Role.MANAGER))

    parameter_name = 'decade'

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '80s':
            return queryset.filter()
