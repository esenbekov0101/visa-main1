from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as srz
from rest_framework.exceptions import NotFound
from rest_framework.fields import empty

from main.models import Payment, History
from main.models import Student
from main.models import Terminal

from .fields import MoneyField


class TerminalLoginObtainPair(srz.Serializer):
    id = srz.IntegerField()
    access_token = srz.IntegerField()

    def validate(self, data):
        try:
            Terminal.objects.get(**data)
            return data
        except Terminal.DoesNotExist:
            raise srz.ValidationError(_('There is no Terminal with these credentials'))

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class TerminalLoginResponseSerializer(srz.Serializer):
    token = srz.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class TerminalStudentCheckSerializer(srz.Serializer):
    phone = srz.CharField()
    name = srz.CharField(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        self.student = None
        super().__init__(instance, data, **kwargs)

    def validate_phone(self, phone):
        try:
            self.student = Student.objects.get(phone=phone)
            return phone
        except Student.DoesNotExist:
            raise NotFound

    def validate(self, attrs):
        attrs['name'] = self.student.fullname
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class TerminalStudentPaySerializer(srz.Serializer):
    id = srz.IntegerField(min_value=1, read_only=True)
    phone = srz.CharField()
    amount = MoneyField()

    def __init__(self, instance=None, data=empty, **kwargs):
        self.student = None
        super().__init__(instance, data, **kwargs)

    def validate_phone(self, phone):
        try:
            self.student = Student.objects.get(phone=phone)
        except Student.DoesNotExist:
            raise NotFound

        return phone

    @atomic
    def create(self, validated_data):
        self.student.balance += validated_data['amount']
        self.student.save()
        self.fields.pop('phone')
        History.objects.create(
            student=self.student,
            description=f'Студент совершил платеж в размере '
                        f'{validated_data["amount"]} сом',
            manager=self.context['request'].terminal.name,
        )
        return Payment.objects.create(amount=self.validated_data['amount'],
                                      terminal=self.context['request'].terminal,
                                      student=self.student)

    def update(self, instance, validated_data):
        raise NotImplementedError()


class TerminalStudentPayResponseSerializer(srz.Serializer):
    id = srz.IntegerField(min_value=1, read_only=True)
    amount = MoneyField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()
