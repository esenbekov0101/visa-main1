from django import forms
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _

from main.models import Book
from main.models import History
from main.models import Payment
from main.models import Terminal


class TerminalForm(forms.ModelForm):
    access_token = forms.IntegerField(min_value=10000)

    class Meta:
        model = Terminal
        exclude = ()


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        exclude = ()

    @atomic
    def save(self, commit=True):
        instance = super(PaymentForm, self).save(commit)
        student = instance.student
        student.balance += instance.amount
        student.save()
        History.objects.create(
            student=student,
            description=f'Владелец совершил платеж в размере {instance.amount} сом',
            manager=instance.terminal.name,
        )
        return instance


class BookChangeForm(forms.ModelForm):
    add_book = forms.IntegerField(min_value=1, max_value=1000, required=False)

    class Meta:
        model = Book
        exclude = ()

    def save(self, commit=True):
        add_book = self.cleaned_data.pop('add_book', None)
        if add_book:
            self.instance.count += add_book
        return super().save(commit)
