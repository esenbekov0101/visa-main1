from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSetMixin

from ..filters import FilterBackend
from ..filters import BookFilter
from .. import models
from .. import permissions as perm
from .. import serializers as srz


class InventoryViewSet(
    ViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView,
):
    pagination_class = None
    permission_classes = (IsAuthenticated, perm.HasBranch)

    srz_map = {
        'list': srz.InventoryListSrz,
    }

    def get_serializer_class(self):
        return self.srz_map.get(self.action, srz.InventoryListSrz)

    def get_queryset(self):
        return models.Inventory.objects.filter(responsible=self.request.user)


class BookViewSet(
    ViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView,
):
    pagination_class = None
    permission_classes = (IsAuthenticated, perm.HasBranch)
    filter_backends = (FilterBackend, )
    filterset_class = BookFilter

    srz_map = {
        'list': srz.BookListSrz,
    }

    def get_serializer_class(self):
        return self.srz_map.get(self.action, srz.BookListSrz)

    def get_queryset(self):
        return models.Book.objects.filter(branch=self.request.user.branch)
