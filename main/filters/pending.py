from django_filters.rest_framework import FilterSet

from .. import models


class PendingFilter(FilterSet):

    class Meta:
        model = models.Pending
        fields = {
            'subject': ['exact'],
            'days_type': ['exact'],
            'start_time': ['exact'],
        }
