from rest_framework import serializers as srz

from main.models import Book
from main.models import Inventory


class InventoryListSrz(srz.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('id', 'name')


class BookListSrz(srz.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'name', 'count', 'price')
