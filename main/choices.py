from django.db.models import IntegerChoices
from django.db.models import TextChoices

from django.utils.translation import gettext_lazy as _


class Role(TextChoices):
    MANAGER = 'manager', _('manager')
    OPERATOR = 'operator', _('operator')
    OWNER = 'owner', _('owner')
    TEACHER = 'teacher', _('teacher')


class Day(IntegerChoices):
    Mon = 0, _('Monday')
    Tu = 1, _('Tuesday')
    We = 2, _('Wednesday')
    Th = 3, _('Thursday')
    Fr = 4, _('Friday')
    Sat = 5, _('Saturday')
    Sa = 6, _('Sunday')


class Time(IntegerChoices):
    EIGHT = 8, '8:00 - 9:00'
    NINE = 9, '9:00 - 10:00'
    TEN = 10, '10:00 - 11:00'
    ELEVEN = 11, '11:00 - 12:00'
    TWELVE = 12, '12:00 - 13:00'
    THIRTEEN = 13, '13:00 - 14:00'
    FOURTEEN = 14, '14:00 - 15:00'
    FIFTEEN = 15, '15:00 - 16:00'
    SIXTEEN = 16, '16:00 - 17:00'
    SEVENTEEN = 17, '17:00 - 18:00'
    EIGHTEEN = 18, '18:00 - 19:00'
    NINETEEN = 19, '19:00 - 20:00'
    TWENTY = 20, '20:00 - 21:00'


class Promoter(TextChoices):
    INSTAGRAM = ('instagram', _('instagram'))
    FRIEND = ('friend', _('friend'))
    BANNERS = ('banners', _('banners'))
    PARTNERS = ('partners', _('partners'))
    USED_TO_GO = ('used_to_go', _('used to go'))
    INTERNET = ('internet', _('internet'))


class Plan(IntegerChoices):
    TRIAL = 1, _('trial')
    ADDITIONAL = 2, _('additional')


class TaskStatus(TextChoices):
    PENDING = 'pending', _('pending')
    STARTED = 'started', _('started')
    SUCCESS = 'success', _('success')
    FAILURE = 'failure', _('failure')
    RETRY = 'retry', _('retry')
    REVOKED = 'revoked', _('revoked')
