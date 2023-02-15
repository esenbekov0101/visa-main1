from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


phone_regex_kg = RegexValidator(regex=r'^996\d{9}$',
                                message=_('Phone number must be in the format: 996XXX123456.'))
