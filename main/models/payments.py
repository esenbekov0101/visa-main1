from django.db import models
from django.utils.translation import gettext_lazy as _

from main.models import Group
from main.models.fields import MoneyField


class Terminal(models.Model):
    name = models.CharField(_('name'), max_length=255)
    address = models.CharField(_('address'), max_length=255)
    access_token = models.PositiveIntegerField(_('access token'))

    class Meta:
        verbose_name = _('terminal')
        verbose_name_plural = _('terminals')

    def __str__(self):
        return self.name


class Payment(models.Model):
    amount = MoneyField(_('amount'), max_digits=22)
    terminal = models.ForeignKey(Terminal, models.SET_NULL, null=True)
    student = models.ForeignKey('Student', models.SET_NULL, null=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')


class EarningRate(models.Model):
    teacher = models.ForeignKey('User', models.CASCADE, verbose_name=_('teacher'))
    group = models.ForeignKey(Group, models.CASCADE, verbose_name=_('group'))
    rate = MoneyField(_('rate'), max_digits=4)

    class Meta:
        verbose_name = _('earning rate')
        verbose_name_plural = _('earning rates')
